# ============================================
# AZURE RESOURCE & COST CHECKER
# Use this to ensure your $100 credits are safe!
# ============================================

Write-Host "--- Scanning for Paid Azure Resources ---" -ForegroundColor Cyan

# 1. Check for App Service Plans (The #1 cost)
$plans = az appservice plan list --query "[].{Name:name, SKU:sku.name, Group:resourceGroup}" -o json | ConvertFrom-Json
if ($plans) {
    Write-Host "[!] FOUND PAID PLANS (Billing Daily):" -ForegroundColor Red
    $plans | Format-Table
} else {
    Write-Host "[OK] No active App Service Plans found." -ForegroundColor Green
}

# 2. Check for Container Registries
$registries = az acr list --query "[].{Name:name, SKU:sku, Group:resourceGroup}" -o json | ConvertFrom-Json
if ($registries) {
    Write-Host "[!] FOUND CONTAINER REGISTRIES (Small Storage Cost):" -ForegroundColor Yellow
    $registries | Format-Table
} else {
    Write-Host "[OK] No Container Registries found." -ForegroundColor Green
}

# 3. Check for SQL Databases (Another common accidentally-left-on cost)
$sql = az sql server list --query "[].{Server:name, Group:resourceGroup}" -o json | ConvertFrom-Json
if ($sql) {
    Write-Host "[!] FOUND SQL SERVERS (Expensive):" -ForegroundColor Red
    $sql | Format-Table
} else {
    Write-Host "[OK] No SQL Servers found." -ForegroundColor Green
}

# 4. Total Resource Group Count
$groups = az group list --query "[].name" -o tsv
if ($groups) {
    Write-Host "--- Overall Resource Summary ---" -ForegroundColor Cyan
    Write-Host "You still have $($groups.Count) Resource Groups in Azure." -ForegroundColor White
    foreach ($g in $groups) {
        $count = (az resource list --resource-group $g --query "length(@)")
        Write-Host " - Group '$g' contains $count resources."
    }
} else {
    Write-Host "Success: Your Azure account is completely empty!" -ForegroundColor Green
}

Write-Host ""
Write-Host "TIP: If you see ANY resources above, they might be using your $100 credits." -ForegroundColor Yellow
Write-Host "To clear them, run: az group delete --name YOUR_GROUP_NAME --yes" -ForegroundColor Gray


