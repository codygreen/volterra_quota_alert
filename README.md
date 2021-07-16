# Volterra Quota Alert

Alert if the Volterra tenant is reaching quota limitations. This script will query the Volterra system quota API and return any quota object that is above the desired threshold (90% by default).

Note: The script does not return any quota object that has a limit less then 0 or equal to 1, such as OIDC provider.

# Requirements

The following environment variables are required:

- VOLT_TENANT_NAME: Volterra Tenant Name
- VOLT_TENANT_API_TOKEN: Volterra API Token

# Run

```
pip install requirements.txt
python3 main.py
```
