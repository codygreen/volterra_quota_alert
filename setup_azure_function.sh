#!/bin/bash

## SET VARIABLES TO YOUR VALUES
postfix=tenantabc
region=centralus
VoltTenantName="your_tenant_name"
VoltTenantApiToken="your_tenant_api_token"
TeamsWebhookUrl="your_teams_webhook_url"
## DO NOT EDIT BEYOND THIS POINT
resourceGroupName=voltMgmt$postfix
storageName=voltmgmt$postfix
keyVaultName=voltmgmt$postfix
functionAppName=voltQuotaAlert$postfix

# Create a resource group.
az group create --name $resourceGroupName --location $region

# Create an Azure storage account in the resource group.
az storage account create \
  --name $storageName \
  --location $region \
  --resource-group resourceGroupName \
  --sku Standard_LRS

# Create Azure Key Vault
az keyvault create \
    --name $keyVaultName \
    --resource-group $resourceGroupName \
    --location $region

# Add required variables to Key Vault as secrets
az keyvault secret set \
--vault-name $keyVaultName \
--name "VoltTenantName" \
--value $VoltTenantName

az keyvault secret set \
--vault-name $keyVaultName \
--name "VoltTenantApiToken" \
--value $VoltTenantApiToken

az keyvault secret set \
--vault-name $keyVaultName \
--name "TeamsWebhookUrl" \
--value $TeamsWebhookUrl

# Create a serverless function app in the resource group.
az functionapp create \
  --name $functionAppName \
  --storage-account $storageName \
  --consumption-plan-location $region \
  --resource-group $resourceGroupName \
  --os-type linux \
  --functions-version 3 \
  --runtime python

# Enable Identity for the Function App
az functionapp identity assign \
    --resource-group $resourceGroupName \
    --name $functionAppName

# Enable access to key vault
principalId=$(az functionapp identity show \
    --resource-group $resourceGroupName \
    --name $functionAppName \
    --query principalId \
    -o tsv)

az keyvault set-policy \
    --name $keyVaultName \
    --resource-group $resourceGroupName \
    --object-id $principalId \
    --secret-permissions get list


# Map secret to requirement environment variables
VoltTenantNameSecretUri=$(az keyvault secret show --vault-name $keyVaultName --name VoltTenantName --query id -o tsv)
VoltTenantApiTokenSecretUri=$(az keyvault secret show --vault-name $keyVaultName --name VoltTenantApiToken --query id -o tsv)
teamsWebhookSecretUri=$(az keyvault secret show --vault-name $keyVaultName --name TeamsWebhookUrl --query id -o tsv)
az functionapp config appsettings set \
    --name $functionAppName \
    --resource-group $resourceGroupName \
    --settings "VoltTenantName=@Microsoft.KeyVault(SecretUri=$VoltTenantNameSecretUri)"
az functionapp config appsettings set \
    --name $functionAppName \
    --resource-group $resourceGroupName \
    --settings "VoltTenantApiToken=@Microsoft.KeyVault(SecretUri=$VoltTenantApiTokenSecretUri)"
az functionapp config appsettings set \
    --name $functionAppName \
    --resource-group $resourceGroupName \
    --settings "TeamsWebhookUrl=@Microsoft.KeyVault(SecretUri=$teamsWebhookSecretUri)"