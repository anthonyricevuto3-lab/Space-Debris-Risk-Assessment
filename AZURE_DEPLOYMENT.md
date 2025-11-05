# Space Debris Risk Assessment - Azure Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the Space Debris Risk Assessment system to Azure Web Apps.

## 📋 Prerequisites

- Azure subscription
- GitHub repository (already set up)
- Azure CLI (optional, for command line deployment)

## 🔧 Azure Web App Setup

### Option 1: Azure Portal (Recommended)

1. **Create Azure Web App:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource" → "Web App"
   - Configure:
     - **App name:** `space-debris-dashboard` (or your preferred name)
     - **Runtime stack:** Python 3.11
     - **Operating System:** Linux
     - **Region:** Your preferred region

2. **Get Publish Profile:**
   - Go to your Web App in Azure Portal
   - Click "Get publish profile" and download the file
   - Copy the entire content of the `.publishsettings` file

3. **Configure GitHub Secrets:**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste the entire publish profile content
   - Click "Add secret"

### Option 2: Azure CLI

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name space-debris-rg --location eastus

# Create App Service plan
az appservice plan create --name space-debris-plan --resource-group space-debris-rg --sku B1 --is-linux

# Create Web App
az webapp create --resource-group space-debris-rg --plan space-debris-plan --name space-debris-dashboard --runtime "PYTHON|3.11"

# Get publish profile
az webapp deployment list-publishing-profiles --name space-debris-dashboard --resource-group space-debris-rg --xml
```

## 🔄 Deployment Process

### Automatic Deployment (GitHub Actions)

Once secrets are configured, deployment happens automatically:

1. Push to `main` branch triggers the workflow
2. GitHub Actions builds the application
3. Deploys to Azure Web App
4. Available at: `https://space-debris-dashboard.azurewebsites.net`

### Manual Deployment

If you prefer manual deployment:

```bash
# Install Azure CLI
# Login to Azure
az login

# Deploy from local directory
az webapp up --name space-debris-dashboard --resource-group space-debris-rg --runtime "PYTHON:3.11"
```

## 🌐 Application URLs

After successful deployment:

- **Main Dashboard:** `https://space-debris-dashboard.azurewebsites.net/`
- **API Health:** `https://space-debris-dashboard.azurewebsites.net/health`
- **Top Risks API:** `https://space-debris-dashboard.azurewebsites.net/api/top-risks`

## 🔍 Features Deployed

- ✅ Real-time TLE data processing from CelesTrak
- ✅ Modern glass-morphism dashboard
- ✅ Space debris risk assessment (0-5 scale)
- ✅ Top 3 highest risk objects display
- ✅ Responsive design for all devices
- ✅ ASCII-compliant for CI/CD compatibility

## 📊 Monitoring

Monitor your deployment:
- Azure Portal → Your Web App → Monitoring
- Logs available in Azure Portal
- Health check: `/health` endpoint

## 🔧 Configuration

Environment variables (set in Azure Portal):
- `PORT`: Automatically set by Azure
- `FLASK_ENV`: Set to `production`

## 🚨 Troubleshooting

### Common Issues:

1. **Deployment fails with credential error:**
   - Ensure `AZURE_WEBAPP_PUBLISH_PROFILE` secret is correctly set
   - Re-download publish profile if needed

2. **App doesn't start:**
   - Check logs in Azure Portal
   - Verify Python version compatibility
   - Ensure all dependencies in requirements.txt

3. **API returns errors:**
   - Check CelesTrak connectivity
   - Verify external network access is allowed

### Getting Help:

- Check GitHub Actions logs for deployment issues
- Azure Portal → Your Web App → Diagnose and solve problems
- Review application logs in Azure Portal

## 🔐 Security Notes

- Publish profiles contain sensitive credentials
- Keep GitHub secrets secure
- Regularly rotate publish profiles
- Monitor Azure costs and usage

## 📈 Scaling

For production use:
- Consider upgrading to Standard or Premium App Service Plan
- Enable Application Insights for monitoring
- Set up custom domains and SSL certificates
- Configure backup and disaster recovery

---

**Status:** ✅ Ready for deployment
**Last Updated:** November 2025
**CI/CD:** Fully operational with ASCII compliance