# 🚀 Azure ML Deployment Guide
## Space Debris Earth Impact Risk Assessment

This guide walks you through deploying the Space Debris Risk Assessment application to Azure Machine Learning.

## 📋 Prerequisites

1. **Azure CLI** - Already installed ✅
2. **Azure Account** - Already logged in ✅
3. **Subscription** - `8d1e82fa-4fb3-48ee-99a2-b3f5784287a2` ✅
4. **Existing Resources** - All resources already exist ✅

## 🏗️ Deployment Architecture

```
Azure ML Workspace: Space-Debris-Risk-Assessment
├── Environment: space-debris-env (Python 3.11 + dependencies)
├── Model: space-debris-risk-model (your application code)
├── Endpoint: space-debris-endpoint (public REST API)
└── Deployment: space-debris-deployment (Standard_DS3_v2)
```

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)
```bash
# Install Azure ML Python SDK
pip install azure-ai-ml azure-identity

# Run automated deployment
python deploy_azure.py
```

### Option 2: Manual Deployment Steps

#### Step 1: Install Azure ML SDK
```bash
pip install azure-ai-ml azure-identity azure-mgmt-ml
```

#### Step 2: Create/Verify Workspace
```bash
# Create resource group (if needed)
az group create --name "Space-Debris-Risk-Assessment-RG" --location "westus3"

# The workspace should already exist with your provided resources
```

#### Step 3: Deploy using Python SDK
```python
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint, 
    ManagedOnlineDeployment,
    Model,
    Environment
)
from azure.identity import DefaultAzureCredential

# Connect to workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
    resource_group_name="Space-Debris-Risk-Assessment-RG", 
    workspace_name="Space-Debris-Risk-Assessment"
)

# Deploy (see deploy_azure.py for full script)
```

## 📊 Configuration Files

- **`azureml-workspace.yml`** - Workspace configuration
- **`environment.yml`** - Environment definition
- **`endpoint.yml`** - Endpoint configuration  
- **`deployment.yml`** - Deployment settings
- **`score.py`** - Inference script
- **`env/conda.yml`** - Python dependencies

## 🧪 Testing the Deployment

### After Deployment:
```bash
# Test the endpoint
python test_endpoint.py

# Or test manually with curl:
curl -X POST "https://[your-endpoint].westus3.inference.ml.azure.com/score" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [your-key]" \
  -d '{"max_pairs": 10, "format": "summary"}'
```

### Sample Request:
```json
{
  "max_pairs": 50,
  "format": "summary",
  "satellite_ids": [22675, 34958]  // Optional: specific satellites
}
```

### Sample Response:
```json
{
  "status": "success",
  "total_assessments": 50,
  "satellites_loaded": 598,
  "top_risks": [
    {
      "rank": 1,
      "satellite_1": "COSMOS 2251",
      "satellite_2": "COSMOS 2251 DEB",
      "risk_score": 2.291,
      "impact_probability_percent": 45.81,
      "risk_level": "MEDIUM"
    }
  ],
  "results": "formatted output based on request format"
}
```

## ⚙️ Configuration Details

### Compute Configuration:
- **Instance Type**: Standard_DS3_v2 (4 cores, 14GB RAM)
- **Instance Count**: 1 (can be scaled)
- **Request Timeout**: 90 seconds
- **Max Concurrent Requests**: 1 per instance

### Environment:
- **Base Image**: Azure ML Ubuntu 20.04
- **Python**: 3.11
- **Key Dependencies**: sgp4, poliastro, astropy, numpy, scipy

## 📈 Monitoring & Scaling

### Monitor Performance:
1. Go to Azure ML Studio
2. Navigate to Endpoints → space-debris-endpoint
3. View metrics, logs, and performance data

### Scale Deployment:
```bash
# Increase instance count
az ml online-deployment update \
  --name space-debris-deployment \
  --endpoint-name space-debris-endpoint \
  --instance-count 3
```

## 🔧 Troubleshooting

### Common Issues:

1. **Environment Build Fails**
   - Check conda.yml dependencies
   - Verify all packages are available in conda-forge

2. **Deployment Timeout**
   - Increase request timeout in deployment.yml
   - Consider using smaller max_pairs for testing

3. **Memory Issues**
   - Upgrade to Standard_DS4_v2 (8 cores, 28GB RAM)
   - Optimize TLE data loading in score.py

4. **Authentication Errors**
   - Verify API key is correct
   - Check endpoint URL format

### Debug Commands:
```bash
# Check deployment status
az ml online-deployment show -n space-debris-deployment -e space-debris-endpoint

# View deployment logs
az ml online-deployment get-logs -n space-debris-deployment -e space-debris-endpoint

# List endpoints
az ml online-endpoint list
```

## 💰 Cost Optimization

- **Development**: Use Standard_DS2_v2 (2 cores, 7GB RAM)
- **Production**: Use Standard_DS3_v2 (4 cores, 14GB RAM)
- **High Load**: Scale horizontally with multiple instances

Estimated costs (West US 3):
- Standard_DS2_v2: ~$0.10/hour
- Standard_DS3_v2: ~$0.20/hour

## 🔒 Security

- **Authentication**: Key-based (can upgrade to Azure AD)
- **Network**: Public endpoint (can configure private)
- **Data**: No data stored, real-time processing only

## 📝 Next Steps

1. **Deploy**: Run `python deploy_azure.py`
2. **Test**: Use `python test_endpoint.py`  
3. **Monitor**: Check Azure ML Studio
4. **Scale**: Adjust based on usage patterns
5. **Integrate**: Use endpoint in your applications

## 🆘 Support

For deployment issues:
1. Check Azure ML Studio logs
2. Verify all resource names match exactly
3. Ensure subscription has sufficient quotas
4. Test locally first with `python test_ml_app.py`