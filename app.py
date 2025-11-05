"""
Main entry point for Azure App Service
Uses standalone space debris risk assessment app
"""

from app_standalone import app

if __name__ == '__main__':
    import os
    # Get port from environment variable (Azure sets this)
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Space Debris Risk Assessment API on port {port}")
    
    # Start the app
    app.run(host='0.0.0.0', port=port, debug=False)