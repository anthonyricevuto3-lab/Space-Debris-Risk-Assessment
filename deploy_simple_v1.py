"""
Simple Azure ML Deployment Script
Using Azure ML SDK v1 for better compatibility
"""

import os
from azureml.core import Workspace, Environment, Model
from azureml.core.webservice import AciWebservice
from azureml.core.model import InferenceConfig

def deploy_simple():
    """Deploy the space debris model to Azure ML with minimal dependencies"""
    
    print("Starting simple Azure ML deployment...")
    
    # Connect to workspace manually
    try:
        ws = Workspace(
            subscription_id="8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
            resource_group="Space-Debris-Risk-Assessment-RG", 
            workspace_name="Space-Debris-Risk-Assessment"
        )
        print(f"Connected to workspace: {ws.name}")
    except Exception as e:
        print(f"Error connecting to workspace: {e}")
        return False
    
    # Create a simple environment
    print("Creating simple environment...")
    env = Environment(name="space-debris-simple")
    env.python.conda_dependencies.add_pip_package("requests>=2.31.0")
    env.python.conda_dependencies.add_pip_package("numpy>=1.24.0")
    env.python.conda_dependencies.add_pip_package("scipy>=1.10.0")
    env.python.conda_dependencies.add_pip_package("pandas>=2.0.0")
    env.python.conda_dependencies.add_pip_package("scikit-learn>=1.3.0")
    env.python.conda_dependencies.add_pip_package("flask>=2.3.0")
    env.python.conda_dependencies.add_pip_package("sgp4>=2.20")
    
    # Register the environment
    env.register(workspace=ws)
    print("Environment registered")
    
    # Create inference configuration
    inference_config = InferenceConfig(
        entry_script="score.py",
        environment=env
    )
    
    # Configure deployment
    deployment_config = AciWebservice.deploy_configuration(
        cpu_cores=1,
        memory_gb=2,
        description="Space Debris Risk Assessment API"
    )
    
    # Deploy the service
    try:
        print("Starting deployment...")
        service = Model.deploy(
            workspace=ws,
            name="space-debris-api",
            models=[],  # We'll use the code directly
            inference_config=inference_config,
            deployment_config=deployment_config,
            overwrite=True
        )
        
        # Wait for deployment to complete
        service.wait_for_deployment(show_output=True)
        print(f"Deployment successful! Endpoint: {service.scoring_uri}")
        return True
        
    except Exception as e:
        print(f"Deployment error: {e}")
        return False

if __name__ == "__main__":
    success = deploy_simple()
    if success:
        print("✅ Azure ML deployment completed successfully!")
    else:
        print("❌ Azure ML deployment failed")