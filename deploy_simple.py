#!/usr/bin/env python3
"""
Simple Azure ML deployment script for Space Debris Risk Assessment.
"""

import os
import sys
import subprocess

def run_command(command: str) -> None:
    """Run a command and check for success."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    print("Success")

def main():
    """Main deployment function."""
    print("=== SPACE DEBRIS RISK ASSESSMENT - AZURE ML DEPLOYMENT ===")
    
    # Check if we're in the right directory
    if not os.path.exists("score.py"):
        print("Error: score.py not found. Please run from the correct directory.")
        sys.exit(1)
    
    # Install required packages
    print("Installing Azure ML SDK...")
    run_command(f"{sys.executable} -m pip install azure-ai-ml azure-identity")
    
    # Deploy using Python SDK
    print("Deploying model to Azure ML...")
    
    deployment_script = '''
import sys
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
    
    print("Connected to Azure ML workspace")
    
    # Create environment
    env = Environment(
        name="space-debris-env",
        conda_file="env/conda.yml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )
    ml_client.environments.create_or_update(env)
    print("Environment created/updated")
    
    # Create model
    model = Model(
        name="space-debris-risk-model",
        path="./",
        description="Space Debris Earth Impact Risk Assessment Model"
    )
    ml_client.models.create_or_update(model)
    print("Model registered")
    
    # Create endpoint
    endpoint = ManagedOnlineEndpoint(
        name="space-debris-endpoint",
        description="Endpoint for Space Debris Earth Impact Risk Assessment",
        auth_mode="key"
    )
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print("Endpoint created")
    
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
    print("Deployment created")
    
    # Set traffic allocation
    endpoint.traffic = {"space-debris-deployment": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print("Traffic allocation set")
    
    print("Deployment completed successfully!")
    print("You can test the endpoint using test_endpoint.py")
    
except Exception as e:
    print(f"Deployment failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Write and execute the deployment script
    with open("deploy_temp.py", "w", encoding="utf-8") as f:
        f.write(deployment_script)
    
    try:
        run_command(f"{sys.executable} deploy_temp.py")
        os.remove("deploy_temp.py")
        print("Deployment completed successfully!")
    except Exception as e:
        print(f"Deployment failed: {e}")
        if os.path.exists("deploy_temp.py"):
            os.remove("deploy_temp.py")
        sys.exit(1)

if __name__ == "__main__":
    main()