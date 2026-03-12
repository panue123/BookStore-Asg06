param(
    [int]$MaxWaitSeconds = 240
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database init + migrations" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

function Test-DockerReady {
    try {
        docker ps *> $null
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-DockerReady)) {
    Write-Host "Docker is not running or not accessible." -ForegroundColor Red
    Write-Host "Start Docker Desktop first, then re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[1/5] Starting databases..." -ForegroundColor Cyan
docker compose up -d db-mysql db-postgres

Write-Host ""
Write-Host "[2/5] Waiting for MySQL..." -ForegroundColor Cyan
$mysqlReady = $false
$mysqlChecks = @(
    { docker compose exec -T db-mysql mysqladmin ping -uroot -proot *> $null },
    { docker compose exec -T db-mysql mysqladmin ping -uroot *> $null }
)
$elapsed = 0
while ($elapsed -lt $MaxWaitSeconds) {
    foreach ($check in $mysqlChecks) {
        try {
            & $check
            $mysqlReady = $true
            break
        } catch {
            # try next check
        }
    }

    if ($mysqlReady) {
        Write-Host "MySQL is ready." -ForegroundColor Green
        break
    }

    Start-Sleep -Seconds 2
    $elapsed += 2
}
if (-not $mysqlReady) {
    Write-Host "Timed out waiting for MySQL." -ForegroundColor Red
    docker compose logs db-mysql --tail 80
    exit 1
}

Write-Host ""
Write-Host "[3/5] Waiting for PostgreSQL..." -ForegroundColor Cyan
$elapsed = 0
while ($elapsed -lt $MaxWaitSeconds) {
    try {
        docker compose exec -T db-postgres pg_isready -U postgres *> $null
        Write-Host "PostgreSQL is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
}
if ($elapsed -ge $MaxWaitSeconds) {
    Write-Host "Timed out waiting for PostgreSQL." -ForegroundColor Red
    exit 1
}

$services = @(
    "customer-service",
    "book-service",
    "cart-service",
    "order-service",
    "pay-service",
    "ship-service",
    "staff-service",
    "comment-rate-service",
    "catalog-service",
    "manager-service",
    "recommender-ai-service",
    "api-gateway"
)

Write-Host ""
Write-Host "[4/5] Starting application services..." -ForegroundColor Cyan
docker compose up -d --build

Write-Host ""
Write-Host "[5/5] Running migrations..." -ForegroundColor Cyan
foreach ($svc in $services) {
    Write-Host "Migrating $svc..." -ForegroundColor Cyan
    docker compose exec -T $svc python manage.py migrate --noinput
}

Write-Host ""
Write-Host "Seeding default accounts..." -ForegroundColor Cyan

# Customer admin
docker compose exec -T customer-service python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@bookstore.com','admin123'); print('customer-service: admin/admin123 ready')"

# Staff admin
docker compose exec -T staff-service python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(username='staffadmin').exists() or User.objects.create_superuser('staffadmin','staffadmin@bookstore.com','admin123',role='admin'); print('staff-service: staffadmin/admin123 ready')"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
