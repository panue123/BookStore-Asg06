param(
    [string]$GatewayBase = "http://localhost:8000"
)

$ErrorActionPreference = "Continue"

function Invoke-Api {
    param([string]$Method="POST", [string]$Url, [object]$Body)
    try {
        return Invoke-RestMethod -Method $Method -Uri $Url -Body ($Body | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 15
    } catch { return $null }
}

Write-Host "Restoring internal accounts via auth/register..." -ForegroundColor Cyan

$accounts = @(
    @{ username="manager01";  email="manager@bookstore.vn";   password="manager123"; role="manager" },
    @{ username="staffadmin"; email="admin@bookstore.vn";     password="admin123";   role="staff"   },
    @{ username="staff01";    email="staff01@bookstore.vn";   password="staff123";   role="staff"   },
    @{ username="alice";      email="alice@bookstore.vn";     password="alice123";   role="customer" },
    @{ username="bob";        email="bob@bookstore.vn";       password="bob12345";   role="customer" }
)

foreach ($acc in $accounts) {
    $res = Invoke-Api -Url "$GatewayBase/api/auth/register/" -Body $acc
    if ($res -and $res.user) {
        Write-Host "  CREATED  $($acc.username) role=$($acc.role) cart_id=$($res.user.cart_id)" -ForegroundColor Green
    } else {
        # Already exists — verify login still works
        $login = Invoke-Api -Url "$GatewayBase/api/auth/login/" -Body @{ username=$acc.username; password=$acc.password }
        if ($login -and $login.user) {
            Write-Host "  EXISTS   $($acc.username) role=$($login.user.role)" -ForegroundColor Yellow
        } else {
            Write-Host "  FAILED   $($acc.username)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Accounts ready:" -ForegroundColor Green
Write-Host "  manager01  / manager123  (manager)"  -ForegroundColor White
Write-Host "  staffadmin / admin123    (staff)"    -ForegroundColor White
Write-Host "  staff01    / staff123    (staff)"    -ForegroundColor White
Write-Host "  alice      / alice123    (customer)" -ForegroundColor White
Write-Host "  bob        / bob12345    (customer)" -ForegroundColor White
Write-Host "  UI: http://localhost:8000"            -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
