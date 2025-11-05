# 🔐 GitHub Secrets Configuration Guide

This guide explains how to set up the required secrets for automated deployment to Azure ML.

## 🎯 Required Secrets

### 1. AZURE_CREDENTIALS
Azure Service Principal credentials for GitHub Actions to authenticate with Azure.

**Format (JSON):**
```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "subscriptionId": "8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
  "tenantId": "your-tenant-id"
}
```

**How to create:**
1. Run this Azure CLI command:
```bash
az ad sp create-for-rbac --name "space-debris-github-actions" \
                         --role contributor \
                         --scopes /subscriptions/8d1e82fa-4fb3-48ee-99a2-b3f5784287a2 \
                         --sdk-auth
```

2. Copy the JSON output and add it as `AZURE_CREDENTIALS` secret in GitHub

### 2. AZURE_SUBSCRIPTION_ID
Your Azure subscription ID.

**Value:** `8d1e82fa-4fb3-48ee-99a2-b3f5784287a2`

## 🛠️ Setting Up Secrets in GitHub

1. Go to your repository: https://github.com/anthonyricevuto3-lab/Space-Debris-Risk-Assessment
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value

## 🔧 Verification

To verify your secrets are working:

1. Go to **Actions** tab in your repository
2. Click **🚀 Space Debris Risk Assessment CI/CD**
3. Click **Run workflow** → **Run workflow**
4. Monitor the deployment job for any authentication errors

## 🚨 Security Notes

- Never commit these secrets to your code
- Rotate secrets regularly
- Use least-privilege access for service principals
- Monitor Azure activity logs for unauthorized access

## 🛰️ Azure Resources Access

The service principal needs access to:
- Resource Group: `Space-Debris-Risk-Assessment-RG`
- ML Workspace: `Space-Debris-Risk-Assessment`
- Storage Account: `spacedebrisris4512633738`
- Key Vault: `spacedebrisris9071396964`

## 🔍 Troubleshooting

**Authentication failed:**
- Verify subscription ID is correct
- Check service principal has Contributor role
- Ensure tenant ID matches your Azure tenant

**Resource access denied:**
- Verify resource group name
- Check ML workspace exists in the correct region
- Confirm service principal has ML workspace access