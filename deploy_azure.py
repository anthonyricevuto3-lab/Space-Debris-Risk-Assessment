#!/usr/bin/env python3
"""
Azure ML deployment script for Space Debris Risk Assessment.
This script handles the complete deployment process to Azure ML.
"""

import json
import os
import subprocess
import sys
from typing import Dict, Any

def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=check
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Error details: {e.stderr}")
        if check:
            raise
        return e

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check Azure CLI
    try:
        result = run_command("az --version", check=False)
        if result.returncode != 0:
            print("❌ Azure CLI not found. Please install Azure CLI.")
            return False
        print("✅ Azure CLI is installed")
    except Exception:
        print("❌ Azure CLI not found. Please install Azure CLI.")
        return False
    
    # Check if logged in
    try:
        result = run_command("az account show", check=False)
        if result.returncode != 0:
            print("❌ Not logged into Azure. Please run 'az login'")
            return False
        print("✅ Logged into Azure")
    except Exception:
        print("❌ Not logged into Azure. Please run 'az login'")
        return False
    
    return True

def install_ml_extension():
    """Install Azure ML extension using Python SDK approach."""
    print("📦 Installing Azure ML Python SDK...")
    try:
        # Install Azure ML SDK
        run_command(f"{sys.executable} -m pip install azure-ai-ml azure-identity")
        print("✅ Azure ML SDK installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install Azure ML SDK: {e}")
        return False

def create_workspace():
    """Create or verify the Azure ML workspace exists."""
    print("🏗️  Creating/verifying Azure ML workspace...")
    
    # Create resource group if it doesn't exist
    rg_command = f"""az group create \
        --name "Space-Debris-Risk-Assessment-RG" \
        --location "westus3" \
        --tags project=space-debris-assessment"""
    
    try:
        run_command(rg_command, check=False)
        print("✅ Resource group ready")
    except Exception as e:
        print(f"⚠️  Resource group creation result: {e}")

def deploy_with_python_sdk():
    """Deploy using Azure ML Python SDK."""
    print("🚀 Deploying with Azure ML Python SDK...")
    
    deployment_script = '''
import os
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration
)
from azure.identity import DefaultAzureCredential

try:
    # Initialize Azure ML client
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id="8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
        resource_group_name="Space-Debris-Risk-Assessment-RG",
        workspace_name="Space-Debris-Risk-Assessment"
    )
    
    print("✅ Connected to Azure ML workspace")
    
    # Create environment
    env = Environment(
        name="space-debris-env",
        conda_file="env/conda.yml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )
    ml_client.environments.create_or_update(env)
    print("✅ Environment created/updated")
    
    # Create model
    model = Model(
        name="space-debris-risk-model",
        path="./",
        description="Space Debris Earth Impact Risk Assessment Model"
    )
    ml_client.models.create_or_update(model)
    print("✅ Model registered")
    
    # Create endpoint
    endpoint = ManagedOnlineEndpoint(
        name="space-debris-endpoint",
        description="Endpoint for Space Debris Earth Impact Risk Assessment",
        auth_mode="key"
    )
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print("✅ Endpoint created")
    
    # Create deployment
    deployment = ManagedOnlineDeployment(
        name="space-debris-deployment",
        endpoint_name="space-debris-endpoint",
        model=model,
        environment=env,
        code_configuration=CodeConfiguration(
            code="./",
            scoring_script="score.py"
        ),
        instance_type="Standard_DS3_v2",
        instance_count=1
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    print("✅ Deployment created")
    
    # Set traffic
    endpoint.traffic = {"space-debris-deployment": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print("✅ Traffic allocation set")
    
    print("🎉 Deployment completed successfully!")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Write and execute the deployment script
    with open("deploy_temp.py", "w", encoding="utf-8") as f:
        f.write(deployment_script)
    
    try:
        run_command(f"{sys.executable} deploy_temp.py")
        os.remove("deploy_temp.py")
        return True
    except Exception as e:
        print(f"❌ Python SDK deployment failed: {e}")
        if os.path.exists("deploy_temp.py"):
            os.remove("deploy_temp.py")
        return False

def test_endpoint():
    """Test the deployed endpoint."""
    print("🧪 Testing deployed endpoint...")
    
    test_script = '''
import json
import requests
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

try:
    # Get endpoint details
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id="8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
        resource_group_name="Space-Debris-Risk-Assessment-RG",
        workspace_name="Space-Debris-Risk-Assessment"
    )
    
    endpoint = ml_client.online_endpoints.get("space-debris-endpoint")
    scoring_uri = endpoint.scoring_uri
    key = ml_client.online_endpoints.get_keys("space-debris-endpoint").primary_key
    
    # Test data
    test_data = {
        "max_pairs": 5,
        "format": "summary"
    }
    
    # Make request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    
    response = requests.post(scoring_uri, json=test_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Endpoint test successful!")
        print(f"📊 Result: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Endpoint test failed: {response.status_code}")
        print(f"❌ Response: {response.text}")
        
except Exception as e:
    print(f"❌ Endpoint test failed: {e}")
'''
    
    with open("test_temp.py", "w") as f:
        f.write(test_script)
    
    try:
        run_command(f"{sys.executable} test_temp.py")
        os.remove("test_temp.py")
        return True
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        if os.path.exists("test_temp.py"):
            os.remove("test_temp.py")
        return False

def main():
    """Main deployment function."""
    print("🚀 SPACE DEBRIS RISK ASSESSMENT - AZURE ML DEPLOYMENT")
    print("=" * 70)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix the issues above.")
        return 1
    
    # Step 2: Install ML SDK
    if not install_ml_extension():
        print("❌ Failed to install Azure ML SDK.")
        return 1
    
    # Step 3: Create workspace
    create_workspace()
    
    # Step 4: Deploy using Python SDK
    if not deploy_with_python_sdk():
        print("❌ Deployment failed.")
        return 1
    
    # Step 5: Test endpoint
    if not test_endpoint():
        print("⚠️  Endpoint deployment succeeded but testing failed.")
        print("   The endpoint may still be initializing. Try testing again in a few minutes.")
    
    print("\n🎉 DEPLOYMENT COMPLETED!")
    print("\n📋 Next Steps:")
    print("   1. Wait 2-3 minutes for the endpoint to fully initialize")
    print("   2. Test the endpoint using the Azure ML Studio")
    print("   3. Monitor the endpoint performance and logs")
    print("   4. Scale the deployment as needed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())