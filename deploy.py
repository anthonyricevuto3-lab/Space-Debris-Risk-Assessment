#!/usr/bin/env python3
"""
Simple deployment script for Space Debris Risk Assessment app.
Run this to quickly set up and test the application.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_test():
    """Run a quick test of the application."""
    print("🧪 Running application test...")
    try:
        result = subprocess.run([
            sys.executable, "test_ml_app.py", 
            "--max-pairs", "20", 
            "--format", "summary"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Application test successful!")
            print("\n📋 Test Output:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Application test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main deployment function."""
    print("🚀 Space Debris Risk Assessment - Deployment Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("test_ml_app.py"):
        print("❌ Error: test_ml_app.py not found. Please run this script from the app directory.")
        return 1
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Run test
    if not run_test():
        return 1
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📖 Usage:")
    print("   python test_ml_app.py --max-pairs 100")
    print("   python test_ml_app.py --max-pairs -1  # Process all pairs")
    print("   python test_ml_app.py --format table")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())