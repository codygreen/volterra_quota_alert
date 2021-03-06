# Volterra Quota Alert

Alert if the Volterra tenant is reaching quota limitations. This script will query the Volterra system quota API and return any quota object that is above the desired threshold (90% by default).

Note: The script does not return any quota object that has a limit less then 0 or equal to 1, such as OIDC provider.

# Requirements

The following environment variables are required:

- VoltTenantName: Volterra Tenant Name
- VoltTenantApiToken: Volterra API Token

# Teams Notifications

If you would like a notice to be posted to a Microsoft Teams Channel you'll need to set the following environment variable:

- TeamsWebhookUrl: Webhook URL supplied by Teams Connector Wizard

For information on how to configure a Teams Webhook, check out the Microsoft teams [documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

# Run

```
pip install requirements.txt
python3 main.py
```

# Azure Function Deployment

The VolterraQuotaAlerts folder contains an Azure Function to automate the alerts. The Azure Function is type _timerTrigger_ by default and you can customize the schedule to match your requirements.

## Create Azure Resources

The script below will create the following resource:

- Resource Group
- Storage Account
- Key Vault and Key Vault Secrets
- Function App

Note: You'll need to ensure you have the Azure CLI installed and that you have logged in and selected the right subscription

The variables will need to be set to your values.

There is also an example script in the source code: _setup_azure_function.sh_

```bash
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
az group create --name voltMgmt$postfix --location $region

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
```
