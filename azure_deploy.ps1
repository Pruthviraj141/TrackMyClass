# ============================================
# DEPLOY TO AZURE WITH CUSTOM DOMAIN
# ============================================

$RESOURCE_GROUP = "pruthviraj"
$LOCATION = "southeastasia"
$PLAN_NAME = "ASP-pruthviraj-b112"
$APP_NAME = "trackmyclass"
$ACR_NAME = "trackmyclassreg"
$DOMAIN_NAME = "trackmyclass.tech"
$IMAGE_NAME = "$ACR_NAME.azurecr.io/trackmyclass:v1"
$FIREBASE_PATH = "d:\DEEP learning attandace system\firebase.json"

Write-Host "=== STEP 1/8: Creating Resource Group ===" -ForegroundColor Cyan
az group create --name $RESOURCE_GROUP --location $LOCATION

Write-Host "=== STEP 2/8: Creating Container Registry ===" -ForegroundColor Cyan
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

Write-Host "=== STEP 3/8: Building Docker Image in Cloud ===" -ForegroundColor Cyan
Write-Host "This takes ~10 minutes (building PyTorch in cloud)..." -ForegroundColor Yellow
az acr build --registry $ACR_NAME --image trackmyclass:v1 --file Dockerfile .

Write-Host "=== STEP 4/8: Creating App Service Plan (B1 Linux) ===" -ForegroundColor Cyan
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux

Write-Host "=== STEP 5/8: Creating Web App with Container ===" -ForegroundColor Cyan
$ACR_PASS = (az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --container-image-name "$ACR_NAME.azurecr.io/trackmyclass:v1" --container-registry-url "https://$ACR_NAME.azurecr.io" --container-registry-user $ACR_NAME --container-registry-password $ACR_PASS

Write-Host "=== STEP 6/8: Setting Environment Variables ===" -ForegroundColor Cyan
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings WEBSITES_PORT=8000 ADMIN_USERNAME=admin ADMIN_PASSWORD=admin123 SESSION_SECRET_KEY=98s7a98dsa789face2026 DATABASE_MODE=firebase CORS_ORIGINS=*

Write-Host "=== STEP 7/8: Injecting Firebase Credentials ===" -ForegroundColor Cyan
$firebaseJson = (Get-Content $FIREBASE_PATH -Raw) -replace "`r`n","`n"
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings "FIREBASE_CREDENTIALS_JSON=$firebaseJson"

Write-Host "=== STEP 8/8: Linking Custom Domain ($DOMAIN_NAME) ===" -ForegroundColor Cyan
# This links your domain back automatically
az webapp config hostname add --webapp-name $APP_NAME --resource-group $RESOURCE_GROUP --hostname $DOMAIN_NAME
# Force HTTPS for security
az webapp update --resource-group $RESOURCE_GROUP --name $APP_NAME --set httpsOnly=true

Write-Host "=== Restarting App ===" -ForegroundColor Cyan
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Domain Active: https://$DOMAIN_NAME" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "When done, run: .\azure_destroy.ps1" -ForegroundColor Red
