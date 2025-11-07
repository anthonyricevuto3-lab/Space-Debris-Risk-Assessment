"""
Space Debris Risk Assessment Application Package

A professional Flask application for space debris risk assessment
using hybrid AI models and real-time orbital data.
"""

from flask import Flask
from flask_cors import CORS
import os
import warnings

from .config import Config, DevelopmentConfig, ProductionConfig

warnings.filterwarnings('ignore')


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name (str): Configuration environment ('development', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        # Auto-detect environment
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            app.config.from_object(ProductionConfig)
        else:
            app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    CORS(app)
    
    # Register blueprints
    from .routes import api_bp, main_bp, init_services
    
    # Initialize services with config
    init_services(app.config)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    return app