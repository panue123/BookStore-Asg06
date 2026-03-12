param(
    [string]$GatewayBase = "http://localhost:8000/api/proxy",
    [int]$WaitSeconds = 120
)

$ErrorActionPreference = "Stop"

function Invoke-ApiGet {
    param([string]$Path)
    return Invoke-RestMethod -Method Get -Uri ("$GatewayBase/$Path") -TimeoutSec 30
}

function Extract-Results {
    param([object]$Data)
    if ($null -eq $Data) { return @() }

    # DRF PageNumberPagination shape: {count,next,previous,results:[...]}
    if ($Data -isnot [System.Array] -and ($Data.PSObject.Properties.Name -contains "results")) {
        $r = $Data.results
        if ($r -is [System.Array]) { return @($r) }
        if ($null -ne $r) { return @($r) }
        return @()
    }

    if ($Data -is [System.Array]) { return @($Data) }
    return @($Data)
}

function Invoke-ApiPost {
    param([string]$Path, [object]$Body)
    $json = $Body | ConvertTo-Json -Depth 10
    return Invoke-RestMethod -Method Post -Uri ("$GatewayBase/$Path") -ContentType "application/json" -Body $json -TimeoutSec 30
}

function Invoke-ApiPatch {
    param([string]$Path, [object]$Body)
    $json = $Body | ConvertTo-Json -Depth 10
    return Invoke-RestMethod -Method Patch -Uri ("$GatewayBase/$Path") -ContentType "application/json" -Body $json -TimeoutSec 30
}

function Wait-Gateway {
    $elapsed = 0
    while ($elapsed -lt $WaitSeconds) {
        try {
            Invoke-ApiGet "books/" *> $null
            Write-Host "API Gateway is ready." -ForegroundColor Green
            return
        } catch {
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
    }
    throw "Timed out waiting for API Gateway at $GatewayBase"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Seed demo data (via API Gateway)" -ForegroundColor Green
Write-Host "Gateway: $GatewayBase" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Wait-Gateway

# --- Publisher + Books (book-service / Postgres) ---
$publishers = @()
try { $publishers = Extract-Results (Invoke-ApiGet "publishers/") } catch { $publishers = @() }
$publisher = $publishers | Where-Object { $_.name -eq "Demo Publisher" } | Select-Object -First 1
if (-not $publisher) {
    $publisher = Invoke-ApiPost "publishers/" @{ name = "Demo Publisher"; address = "HCMC, VN" }
    Write-Host "Created publisher: id=$($publisher.id)" -ForegroundColor Green
} else {
    Write-Host "Publisher exists: id=$($publisher.id)" -ForegroundColor Yellow
}

$bookSpecs = @(
    @{ title = "Clean Code"; author = "Robert C. Martin"; category = "programming"; price = "35.00"; stock = 50 },
    @{ title = "The Pragmatic Programmer"; author = "Andrew Hunt"; category = "programming"; price = "42.00"; stock = 40 },
    @{ title = "Sapiens"; author = "Yuval Noah Harari"; category = "history"; price = "28.00"; stock = 25 },
    @{ title = "A Brief History of Time"; author = "Stephen Hawking"; category = "science"; price = "20.00"; stock = 30 },
    @{ title = "The Great Gatsby"; author = "F. Scott Fitzgerald"; category = "fiction"; price = "12.00"; stock = 60 }
)

$createdBooks = @()
foreach ($spec in $bookSpecs) {
    # Use search endpoint (not paginated) to avoid duplicates even with many books.
    $found = $null
    try {
        $sr = Invoke-ApiGet ("books/search/?q=" + [uri]::EscapeDataString($spec.title))
        $matches = @()
        if ($sr.PSObject.Properties.Name -contains "results") { $matches = @($sr.results) }
        else { $matches = Extract-Results $sr }
        $found = $matches | Where-Object { $_.title -eq $spec.title } | Select-Object -First 1
    } catch { $found = $null }

    if ($found) {
        Write-Host "Book exists: id=$($found.id) title=$($found.title)" -ForegroundColor Yellow
        $createdBooks += $found
        continue
    }

    $body = @{
        title = $spec.title
        author = $spec.author
        publisher = $publisher.id
        category = $spec.category
        price = $spec.price
        stock = $spec.stock
    }
    $newBook = Invoke-ApiPost "books/" $body
    Write-Host "Created book: id=$($newBook.id) title=$($newBook.title)" -ForegroundColor Green
    $createdBooks += $newBook
}

# --- Customer + Cart + Order (customer/cart/order/pay/ship) ---
$addr = Invoke-ApiPost "addresses/" @{ street = "1 Nguyen Hue"; city = "Ho Chi Minh"; country = "Vietnam" }
$job = Invoke-ApiPost "jobs/" @{ title = "Developer"; company = "Demo Co" }

$customer = $null
$customerToken = $null
try {
    $resp = Invoke-ApiPost "customers/" @{
        username = "alice"
        email = "alice@example.com"
        password = "alice123"
        address = $addr.id
        job = $job.id
    }
    $customer = $resp.data
    $customerToken = $resp.token
    Write-Host "Created customer: id=$($customer.id) username=$($customer.username)" -ForegroundColor Green
} catch {
    # If exists, just login and reuse.
    $login = Invoke-ApiPost "customers/login/" @{ username = "alice"; password = "alice123" }
    $customerToken = $login.token
    $customerId = $login.customer_id
    $customer = Invoke-ApiGet ("customers/$customerId/")
    Write-Host "Customer exists: id=$($customer.id) username=$($customer.username)" -ForegroundColor Yellow
}

if (-not $customer.cart_id) {
    $cart = Invoke-ApiPost "carts/" @{ customer_id = $customer.id }
    Invoke-ApiPatch ("customers/$($customer.id)/") @{ cart_id = $cart.id }
    $customer.cart_id = $cart.id
    Write-Host "Created cart and linked to customer: cart_id=$($cart.id)" -ForegroundColor Green
}

# Add 2 items
$book1 = $createdBooks | Select-Object -First 1
$book2 = $createdBooks | Select-Object -Skip 1 -First 1
Invoke-ApiPost ("carts/$($customer.cart_id)/add_item/") @{ book_id = $book1.id; quantity = 1 } *> $null
Invoke-ApiPost ("carts/$($customer.cart_id)/add_item/") @{ book_id = $book2.id; quantity = 2 } *> $null
Write-Host "Added items to cart: cart_id=$($customer.cart_id)" -ForegroundColor Green

$orderResp = Invoke-ApiPost "orders/checkout/" @{
    customer_id = $customer.id
    cart_id = $customer.cart_id
    shipping_address = "1 Nguyen Hue, Ho Chi Minh, Vietnam"
    payment_method = "credit_card"
}
$order = $orderResp.order
Write-Host "Created order: id=$($order.id) status=$($order.status)" -ForegroundColor Green

# --- Comment/Rating ---
try {
    $comment = Invoke-ApiPost "comments/" @{
        customer_id = $customer.id
        book_id = $book1.id
        content = "Great book. Highly recommended."
        rating = 5
    }
    Write-Host "Created comment: id=$($comment.id) rating=$($comment.rating)" -ForegroundColor Green
} catch {
    Write-Host "Skipping comment seed (may already exist for this customer/book)." -ForegroundColor Yellow
}

# --- Staff + RBAC + Shift (staff-service / MySQL) ---
$staffAdmin = $null
try {
    $login = Invoke-ApiPost "staff/login/" @{ username = "staffadmin"; password = "admin123" }
    $staffAdmin = $login.staff
    Write-Host "Staff admin exists: id=$($staffAdmin.id)" -ForegroundColor Yellow
} catch {
    $staffAdmin = Invoke-ApiPost "staff/" @{
        username = "staffadmin"
        email = "staffadmin@bookstore.com"
        first_name = "Staff"
        last_name = "Admin"
        password = "admin123"
        role = "admin"
        department = "HQ"
    }
    Write-Host "Created staff admin: id=$($staffAdmin.id)" -ForegroundColor Green
}

function Ensure-StaffUser {
    param([string]$Username, [string]$Role, [string]$Department)
    try {
        $login = Invoke-ApiPost "staff/login/" @{ username = $Username; password = "admin123" }
        if ($login.staff) { return $login.staff }
    } catch {
        # continue to create
    }

    $resp = Invoke-ApiPost "staff/create_staff/" @{
        requester_id = $staffAdmin.id
        username = $Username
        password = "admin123"
        email = "$Username@bookstore.com"
        role = $Role
        department = $Department
    }
    if ($resp.staff) { return $resp.staff }
    return $resp
}

$manager1 = Ensure-StaffUser -Username "manager1" -Role "manager" -Department "Management"
$ship1 = Ensure-StaffUser -Username "ship1" -Role "shipping" -Department "Shipping"
$inv1 = Ensure-StaffUser -Username "inv1" -Role "inventory" -Department "Inventory"
Write-Host "Ensured staff users: manager1, ship1, inv1" -ForegroundColor Green

try {
    $start = (Get-Date).AddHours(1).ToString("s")
    $end = (Get-Date).AddHours(9).ToString("s")
    $shiftResp = Invoke-ApiPost "staff/create_shift/" @{
        requester_id = $staffAdmin.id
        staff = $ship1.id
        start_time = $start
        end_time = $end
        notes = "Demo shift"
    }
    Write-Host "Created shift: id=$($shiftResp.shift.id) staff_id=$($shiftResp.shift.staff)" -ForegroundColor Green
} catch {
    Write-Host "Skipping shift seed (may already exist or migrations not applied yet)." -ForegroundColor Yellow
}

# --- Recommendations ---
try {
    $recs = Invoke-ApiGet ("recommendations/get_recommendations/?customer_id=$($customer.id)&limit=5")
    Write-Host "Recommendations ready: $($recs.recommendations.Count) items" -ForegroundColor Green
} catch {
    Write-Host "Recommendation call failed (service might still be warming up)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Seed completed." -ForegroundColor Green
