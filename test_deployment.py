#!/usr/bin/env python3
"""
Local deployment test script for Space Debris Risk Assessment
Tests the application before Azure deployment
"""

import subprocess
import time
import requests
import sys
import os

def test_application():
    """Test the application locally"""
    print("* Testing Space Debris Risk Assessment Application")
    print("=" * 60)
    
    # Test 1: Check Python files for syntax errors
    print("\n1. Testing Python syntax...")
    try:
        subprocess.run([sys.executable, "-m", "py_compile", "app_standalone.py"], check=True)
        subprocess.run([sys.executable, "-m", "py_compile", "main.py"], check=True)
        subprocess.run([sys.executable, "-m", "py_compile", "app.py"], check=True)
        print("SUCCESS: All Python files compile successfully")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Python syntax error: {e}")
        return False
    
    # Test 2: Check dependencies
    print("\n2. Testing dependencies...")
    try:
        import flask
        import requests
        import numpy
        import pandas
        print("SUCCESS: All required dependencies available")
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        return False
    
    # Test 3: Test Flask app creation
    print("\n3. Testing Flask app creation...")
    try:
        from app_standalone import app
        print("SUCCESS: Flask app created successfully")
    except Exception as e:
        print(f"ERROR: Flask app creation failed: {e}")
        return False
    
    # Test 4: Test routes
    print("\n4. Testing application routes...")
    try:
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("SUCCESS: Health endpoint working")
            else:
                print(f"ERROR: Health endpoint failed: {response.status_code}")
                return False
            
            # Test API endpoint
            response = client.get('/api/top-risks')
            if response.status_code == 200:
                data = response.get_json()
                if isinstance(data, list) and len(data) >= 1:
                    print(f"SUCCESS: API endpoint working ({len(data)} objects returned)")
                else:
                    print("WARNING: API endpoint returns empty data (may be normal)")
            else:
                print(f"ERROR: API endpoint failed: {response.status_code}")
                return False
            
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("SUCCESS: Home page working")
            else:
                print(f"ERROR: Home page failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Route testing failed: {e}")
        return False
    
    # Test 5: Check for ASCII compliance
    print("\n5. Testing ASCII compliance...")
    import re
    
    files_to_check = ['app_standalone.py', 'main.py', 'app.py']
    ascii_compliant = True
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'[^\x00-\x7F]', content):
                    print(f"ERROR: {filename} contains non-ASCII characters")
                    ascii_compliant = False
                else:
                    print(f"SUCCESS: {filename} is ASCII compliant")
    
    if not ascii_compliant:
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: ALL TESTS PASSED!")
    print("SUCCESS: Application is ready for Azure deployment")
    print("\nNext steps:")
    print("1. Configure Azure Web App")
    print("2. Set up GitHub secrets (AZURE_WEBAPP_PUBLISH_PROFILE)")
    print("3. Push to main branch to trigger deployment")
    print("4. Monitor deployment in GitHub Actions")
    
    return True

if __name__ == '__main__':
    success = test_application()
    sys.exit(0 if success else 1)