# ============================================
# DESTROY ALL AZURE RESOURCES (Cost = $0)
# ============================================

$RESOURCE_GROUP = "pruthviraj"
$ACR_NAME = "trackmyclassreg"
$APP_NAME = "trackmyclass"
$PLAN_NAME = "ASP-pruthviraj-b112"

Write-Host "Destroying Azure resources to save credits..." -ForegroundColor Yellow

# Step 1: Delete Web App (removes the domain mapping too)
Write-Host "Deleting Web App ($APP_NAME)..." -ForegroundColor Cyan
az webapp delete --resource-group $RESOURCE_GROUP --name $APP_NAME

# Step 2: Delete Container Registry (saves ~$5/month)
Write-Host "Deleting Container Registry ($ACR_NAME)..." -ForegroundColor Cyan
az acr delete --name $ACR_NAME --resource-group $RESOURCE_GROUP --yes

# Step 3: Delete App Service Plan (this is the expensive one ~$13/month)
Write-Host "Deleting App Service Plan ($PLAN_NAME)..." -ForegroundColor Cyan
az appservice plan delete --resource-group $RESOURCE_GROUP --name $PLAN_NAME --yes

# Step 4: Delete Resource Group (removes everything)
Write-Host "Final Resource Group wipeout ($RESOURCE_GROUP)..." -ForegroundColor Cyan
az group delete --name $RESOURCE_GROUP --yes --no-wait

Write-Host ""
Write-Host "ALL RESOURCES DELETED! Monthly cost = $0" -ForegroundColor Green
Write-Host "Your Firebase data (students, attendance) is SAFE in the cloud." -ForegroundColor Green
Write-Host "Run azure_deploy.ps1 whenever you want to go live again!" -ForegroundColor Green
