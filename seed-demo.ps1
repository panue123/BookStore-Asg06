param(
    [string]$GW   = "http://localhost:8000/api",
    [string]$Book = "http://localhost:8002/api",
    [string]$Cart = "http://localhost:8003/api",
    [string]$Cmt  = "http://localhost:8008/api",
    [string]$Staff= "http://localhost:8007/api",
    [string]$Cust = "http://localhost:8001/api",
    [int]$WaitSeconds = 60
)
$ErrorActionPreference = "Stop"

function Invoke-Api {
    param([string]$Method="GET",[string]$Base,[string]$Path,[object]$Body,[string]$Token)
    $uri = "$Base/$Path"
    $headers = @{ "Content-Type"="application/json" }
    if ($Token) { $headers["Authorization"] = "Bearer $Token" }
    $params = @{ Method=$Method; Uri=$uri; Headers=$headers; TimeoutSec=30 }
    if ($Body) { $params["Body"] = ($Body | ConvertTo-Json -Depth 10) }
    return Invoke-RestMethod @params
}

# ── Wait for gateway ───────────────────────────────────────
Write-Host "Waiting for gateway..." -ForegroundColor Cyan
for ($i=0; $i -lt $WaitSeconds; $i+=3) {
    try { Invoke-Api -Base $GW -Path "books/" | Out-Null; Write-Host "Gateway ready!" -ForegroundColor Green; break } catch { Start-Sleep 3 }
}

# ── Publisher & Books (direct to book-service) ─────────────
Write-Host "`n[1] Seeding publisher & books..." -ForegroundColor Cyan
$pub = $null
try {
    $pub = Invoke-Api -Method POST -Base $Book -Path "publishers/" -Body @{name="CloudBooks Press";address="Ho Chi Minh City, VN"}
    Write-Host "  Publisher: id=$($pub.id)" -ForegroundColor Green
} catch {
    try {
        $pubs = Invoke-Api -Base $Book -Path "publishers/"
        $pubList = if ($pubs.results) { $pubs.results } else { $pubs }
        $pub = $pubList | Where-Object { $_.name -eq "CloudBooks Press" } | Select-Object -First 1
        if (-not $pub) { $pub = @{id=1} }
        Write-Host "  Publisher exists: id=$($pub.id)" -ForegroundColor Yellow
    } catch { $pub = @{id=1}; Write-Host "  Using publisher id=1" -ForegroundColor Yellow }
}

$books = @(
  @{title="Clean Code";author="Robert C. Martin";category="programming";price="35.00";stock=50;description="A handbook of agile software craftsmanship."},
  @{title="The Pragmatic Programmer";author="Andrew Hunt";category="programming";price="42.00";stock=40;description="Your journey to mastery."},
  @{title="Design Patterns";author="Gang of Four";category="programming";price="55.00";stock=30;description="Elements of reusable object-oriented software."},
  @{title="Sapiens";author="Yuval Noah Harari";category="history";price="28.00";stock=25;description="A brief history of humankind."},
  @{title="A Brief History of Time";author="Stephen Hawking";category="science";price="20.00";stock=35;description="From the Big Bang to Black Holes."},
  @{title="The Great Gatsby";author="F. Scott Fitzgerald";category="fiction";price="12.00";stock=60;description="The story of the mysteriously wealthy Jay Gatsby."},
  @{title="Introduction to Algorithms";author="Cormen et al.";category="programming";price="65.00";stock=20;description="The classic algorithms textbook."},
  @{title="Cosmos";author="Carl Sagan";category="science";price="22.00";stock=45;description="A personal voyage through the universe."},
  @{title="1984";author="George Orwell";category="fiction";price="15.00";stock=55;description="A dystopian social science fiction novel."},
  @{title="Calculus";author="James Stewart";category="math";price="48.00";stock=18;description="Early transcendentals, 8th edition."}
)

$createdBooks = @()
foreach ($b in $books) {
    $b["publisher"] = $pub.id
    try {
        $nb = Invoke-Api -Method POST -Base $Book -Path "books/" -Body $b
        Write-Host "  Book: id=$($nb.id) '$($nb.title)'" -ForegroundColor Green
        $createdBooks += $nb
    } catch {
        Write-Host "  Skip (exists?): $($b.title)" -ForegroundColor Yellow
    }
}

# If books already existed, fetch them
if ($createdBooks.Count -eq 0) {
    try {
        $existing = Invoke-Api -Base $Book -Path "books/"
        $createdBooks = if ($existing.results) { $existing.results } else { $existing }
        Write-Host "  Loaded $($createdBooks.Count) existing books" -ForegroundColor Yellow
    } catch {}
}

# ── Register customer via gateway ──────────────────────────
Write-Host "`n[2] Registering customer..." -ForegroundColor Cyan
$token = $null; $custUser = $null
try {
    $reg = Invoke-Api -Method POST -Base $GW -Path "auth/register/" -Body @{username="alice";email="alice@bookstore.vn";password="alice123"}
    $token = $reg.access_token; $custUser = $reg.user
    Write-Host "  Registered: username=$($custUser.username) cart_id=$($custUser.cart_id)" -ForegroundColor Green
} catch {
    try {
        $login = Invoke-Api -Method POST -Base $GW -Path "auth/login/" -Body @{username="alice";password="alice123"}
        $token = $login.access_token; $custUser = $login.user
        Write-Host "  Login existing: username=$($custUser.username)" -ForegroundColor Yellow
    } catch { Write-Host "  Auth failed: $_" -ForegroundColor Red }
}

$custId = $custUser.service_user_id
$cartId = $custUser.cart_id

# ── Add to cart ────────────────────────────────────────────
Write-Host "`n[3] Adding items to cart..." -ForegroundColor Cyan
if ($cartId -and $createdBooks.Count -ge 2) {
    try {
        Invoke-Api -Method POST -Base $GW -Path "customers/$custId/updateCart/" -Body @{book_id=$createdBooks[0].id;quantity=1} -Token $token | Out-Null
        Invoke-Api -Method POST -Base $GW -Path "customers/$custId/updateCart/" -Body @{book_id=$createdBooks[1].id;quantity=2} -Token $token | Out-Null
        Write-Host "  Added 2 books to cart $cartId" -ForegroundColor Green
    } catch { Write-Host "  Cart update: $_" -ForegroundColor Yellow }
}

# ── Checkout (Saga) ────────────────────────────────────────
Write-Host "`n[4] Checkout via Saga..." -ForegroundColor Cyan
try {
    $order = Invoke-Api -Method POST -Base $GW -Path "orders/checkout/" -Body @{
        customer_id=$custId; cart_id=$cartId
        shipping_address="123 Nguyen Hue, Q.1, TP.HCM"
        payment_method="credit_card"
    } -Token $token
    Write-Host "  Order id=$($order.order.id) status=$($order.order.status) success=$($order.success)" -ForegroundColor Green
    if ($order.saga_steps) {
        $steps = $order.saga_steps | ForEach-Object { "$($_.step):$($_.status)" }
        Write-Host "  Saga: $($steps -join ', ')" -ForegroundColor Cyan
    }
} catch { Write-Host "  Checkout: $_" -ForegroundColor Yellow }

# ── Comments/Reviews (direct) ──────────────────────────────
Write-Host "`n[5] Adding reviews..." -ForegroundColor Cyan
if ($createdBooks.Count -gt 0) {
    $reviews = @(
      @{customer_id=$custId;book_id=$createdBooks[0].id;content="Cuốn sách tuyệt vời, rất hữu ích!";rating=5},
      @{customer_id=$custId;book_id=$createdBooks[1].id;content="Rất thực tế, áp dụng được ngay.";rating=4}
    )
    foreach ($rev in $reviews) {
        try {
            Invoke-Api -Method POST -Base $Cmt -Path "comments/" -Body $rev | Out-Null
            Write-Host "  Review added for book_id=$($rev.book_id)" -ForegroundColor Green
        } catch { Write-Host "  Skip review book_id=$($rev.book_id)" -ForegroundColor Yellow }
    }
}

# ── Staff admin (direct) ───────────────────────────────────
Write-Host "`n[6] Creating staff admin..." -ForegroundColor Cyan
try {
    $sr = Invoke-Api -Method POST -Base $Staff -Path "staff/" -Body @{
        username="staffadmin";email="admin@bookstore.vn"
        password="admin123";role="admin";department="HQ"
        first_name="Staff";last_name="Admin"
    }
    Write-Host "  Staff admin created: id=$($sr.id)" -ForegroundColor Green
} catch { Write-Host "  Staff admin exists" -ForegroundColor Yellow }

# ── Register 2nd user bob ──────────────────────────────────
Write-Host "`n[7] Registering 2nd user (bob)..." -ForegroundColor Cyan
try {
    $reg2 = Invoke-Api -Method POST -Base $GW -Path "auth/register/" -Body @{username="bob";email="bob@bookstore.vn";password="bob12345"}
    Write-Host "  Registered bob: cart_id=$($reg2.user.cart_id)" -ForegroundColor Green
    # Bob adds a book to cart
    if ($createdBooks.Count -ge 3) {
        Invoke-Api -Method POST -Base $GW -Path "customers/$($reg2.user.service_user_id)/updateCart/" -Body @{book_id=$createdBooks[2].id;quantity=1} -Token $reg2.access_token | Out-Null
        Write-Host "  Bob added book to cart" -ForegroundColor Green
    }
} catch { Write-Host "  Bob exists or failed" -ForegroundColor Yellow }

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Seed completed!" -ForegroundColor Green
Write-Host "  UI:       http://localhost:8000" -ForegroundColor White
Write-Host "  RabbitMQ: http://localhost:15672  (guest/guest)" -ForegroundColor White
Write-Host "  Health:   http://localhost:8000/health/" -ForegroundColor White
Write-Host "  Metrics:  http://localhost:8000/metrics/" -ForegroundColor White
Write-Host "  Login:    alice / alice123" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
