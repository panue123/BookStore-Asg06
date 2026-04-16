param(
    [string]$GatewayBase = "http://localhost:8000",
    [string]$StaffBase = "http://localhost:8007",
    [string]$ManagerBase = "http://localhost:8010"
)

$ErrorActionPreference = "Stop"

function Invoke-Api {
    param(
        [string]$Method,
        [string]$Url,
        [object]$Body = $null
    )

    $params = @{
        Method = $Method
        Uri = $Url
        TimeoutSec = 15
    }

    if ($Body -ne $null) {
        $params["ContentType"] = "application/json"
        $params["Body"] = ($Body | ConvertTo-Json -Depth 8)
    }

    try {
        return Invoke-RestMethod @params
    } catch {
        return $null
    }
}

Write-Host "Ensuring domain users (staff/manager)..." -ForegroundColor Cyan

$staffUsers = @(
    @{ username = "staffadmin"; email = "admin@bookstore.vn"; password = "admin123"; role = "admin"; department = "HQ" },
    @{ username = "staff01"; email = "staff01@bookstore.vn"; password = "staff123"; role = "staff"; department = "Warehouse" }
)

foreach ($u in $staffUsers) {
    $null = Invoke-Api -Method "POST" -Url "$StaffBase/api/staff/" -Body $u
}

$managerBody = @{ name = "manager01"; email = "manager@bookstore.vn"; password = "manager123"; department = "Ops" }
$null = Invoke-Api -Method "POST" -Url "$ManagerBase/api/manager/" -Body $managerBody

$staffList = Invoke-Api -Method "GET" -Url "$StaffBase/api/staff/"
$managerList = Invoke-Api -Method "GET" -Url "$ManagerBase/api/manager/"

if (-not $staffList -or -not $managerList) {
    throw "Could not read staff/manager services. Ensure docker services are running."
}

$staffAdmin = $staffList.results | Where-Object { $_.username -eq "staffadmin" } | Select-Object -First 1
$staff01 = $staffList.results | Where-Object { $_.username -eq "staff01" } | Select-Object -First 1
$manager01 = $managerList.results | Where-Object { $_.name -eq "manager01" } | Select-Object -First 1

if (-not $staffAdmin -or -not $staff01 -or -not $manager01) {
    throw "Missing domain users after create/list check."
}

Write-Host "Syncing auth users and passwords..." -ForegroundColor Cyan

$pythonCode = @"
from app.models import AuthUser, UserRole

records = [
    ('staffadmin', 'admin@bookstore.vn', 'admin123', UserRole.STAFF, $($staffAdmin.id)),
    ('staff01', 'staff01@bookstore.vn', 'staff123', UserRole.STAFF, $($staff01.id)),
    ('manager01', 'manager@bookstore.vn', 'manager123', UserRole.MANAGER, $($manager01.id)),
]

for username, email, password, role, service_user_id in records:
    user, _ = AuthUser.objects.get_or_create(
        username=username,
        defaults={'email': email, 'role': role, 'service_user_id': service_user_id},
    )
    user.email = email
    user.role = role
    user.service_user_id = service_user_id
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f'updated: {username} role={role} service_user_id={service_user_id}')
"@

$dockerCmd = "docker exec bookstore-micro05-auth-service-1 python manage.py shell -c `"$($pythonCode -replace '"','\"')`""
Invoke-Expression $dockerCmd | Out-Host

Write-Host "Verifying login through gateway..." -ForegroundColor Cyan
$checks = @(
    @{ username = "staffadmin"; password = "admin123" },
    @{ username = "staff01"; password = "staff123" },
    @{ username = "manager01"; password = "manager123" }
)

foreach ($c in $checks) {
    $res = Invoke-Api -Method "POST" -Url "$GatewayBase/api/auth/login/" -Body $c
    if ($res -and $res.user) {
        Write-Host ("OK {0} role={1} service_user_id={2}" -f $c.username, $res.user.role, $res.user.service_user_id) -ForegroundColor Green
    } else {
        Write-Host ("FAILED {0}" -f $c.username) -ForegroundColor Red
    }
}

Write-Host "Done." -ForegroundColor Green
