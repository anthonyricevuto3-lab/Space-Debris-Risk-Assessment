#!/usr/bin/env python3
"""
Test script for the deployed Azure ML endpoint.
"""

import json
import requests
import time
from typing import Dict, Any

def test_endpoint():
    """Test the deployed endpoint with sample requests."""
    
    print("🧪 Testing Azure ML Endpoint for Space Debris Risk Assessment")
    print("=" * 70)
    
    # You'll need to replace these with your actual endpoint details after deployment
    SCORING_URI = "https://space-debris-endpoint.westus3.inference.ml.azure.com/score"
    API_KEY = "YOUR_API_KEY_HERE"  # Will be provided after deployment
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "azureml-model-deployment": "space-debris-deployment"
    }
    
    # Test cases
    test_cases = [
        {
            "name": "Quick Assessment",
            "data": {
                "max_pairs": 5,
                "format": "summary"
            }
        },
        {
            "name": "Medium Assessment", 
            "data": {
                "max_pairs": 25,
                "format": "json"
            }
        },
        {
            "name": "Detailed Assessment",
            "data": {
                "max_pairs": 100,
                "format": "summary"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print(f"📊 Parameters: {test_case['data']}")
        
        try:
            start_time = time.time()
            
            # Make request
            response = requests.post(
                SCORING_URI,
                headers=headers,
                json=test_case['data'],
                timeout=120  # 2 minute timeout
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! ({elapsed_time:.2f}s)")
                print(f"📈 Status: {result.get('status', 'unknown')}")
                print(f"📊 Assessments: {result.get('total_assessments', 0)}")
                print(f"🛰️  Satellites: {result.get('satellites_loaded', 0)}")
                
                # Show top risk if available
                if 'top_risks' in result:
                    print(f"🚨 Top Risk: {result['top_risks'][0]['satellite_1']} & {result['top_risks'][0]['satellite_2']}")
                    print(f"   Risk Score: {result['top_risks'][0]['risk_score']:.3f}/5.0 ({result['top_risks'][0]['impact_probability_percent']:.1f}%)")
                
            else:
                print(f"❌ Failed! Status: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out after 2 minutes")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📋 Manual Testing Instructions:")
    print("1. Replace SCORING_URI and API_KEY with actual values from Azure ML Studio")
    print("2. Run this script to test different scenarios")
    print("3. Monitor performance and adjust instance count as needed")

def get_endpoint_info():
    """Get endpoint information from Azure ML."""
    
    info_script = '''
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

try:
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id="8d1e82fa-4fb3-48ee-99a2-b3f5784287a2",
        resource_group_name="Space-Debris-Risk-Assessment-RG",
        workspace_name="Space-Debris-Risk-Assessment"
    )
    
    # Get endpoint details
    endpoint = ml_client.online_endpoints.get("space-debris-endpoint")
    keys = ml_client.online_endpoints.get_keys("space-debris-endpoint")
    
    print("📋 ENDPOINT INFORMATION:")
    print(f"   Name: {endpoint.name}")
    print(f"   Scoring URI: {endpoint.scoring_uri}")
    print(f"   Primary Key: {keys.primary_key}")
    print(f"   Secondary Key: {keys.secondary_key}")
    print(f"   Auth Mode: {endpoint.auth_mode}")
    
    # Update this file with the actual values
    with open(__file__, 'r') as f:
        content = f.read()
    
    content = content.replace(
        'SCORING_URI = "https://space-debris-endpoint.westus3.inference.ml.azure.com/score"',
        f'SCORING_URI = "{endpoint.scoring_uri}"'
    )
    content = content.replace(
        'API_KEY = "YOUR_API_KEY_HERE"',
        f'API_KEY = "{keys.primary_key}"'
    )
    
    with open(__file__, 'w') as f:
        f.write(content)
    
    print("✅ Test script updated with endpoint details")
    
except Exception as e:
    print(f"❌ Failed to get endpoint info: {e}")
'''
    
    exec(info_script)

if __name__ == "__main__":
    # First try to get endpoint info automatically
    try:
        get_endpoint_info()
    except Exception:
        print("⚠️  Could not auto-retrieve endpoint info. Manual configuration needed.")
    
    # Run tests
    test_endpoint()