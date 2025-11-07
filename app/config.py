"""
Configuration module for Space Debris Risk Assessment application.
Author: Anthony Ricevuto - Computer Science Student at CSULB
LinkedIn: https://www.linkedin.com/in/anthony-ricevuto-mle/

Contains environment-specific settings and configuration classes for the
space debris risk assessment system.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'space-debris-risk-assessment-secret-key'
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Application settings
    APP_NAME = 'Space Debris Risk Assessment'
    APP_AUTHOR = 'Anthony Ricevuto'
    APP_VERSION = '2.0.0'
    APP_DESCRIPTION = 'Professional AI-powered space debris risk assessment system'
    
    # API settings
    API_RATE_LIMIT = 100  # requests per minute
    API_TIMEOUT = 30  # seconds
    
    # Data source settings
    CELESTRAK_URLS = [
        'https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=tle',
        'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle',
        'https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=tle'
    ]
    
    # Cache settings
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # ML Model settings
    ML_MODEL_CACHE_SIZE = 1000
    ML_TRAINING_SAMPLES = 5000
    
    # Risk assessment settings
    RISK_SCALE_MAX = 5.0
    RISK_THRESHOLD_HIGH = 3.5
    RISK_THRESHOLD_MEDIUM = 2.0
    
    # Orbital mechanics constants
    EARTH_RADIUS_KM = 6371.0
    EARTH_MU = 398600.4418  # Earth's gravitational parameter
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # More verbose logging for development
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed rate limiting for development
    API_RATE_LIMIT = 1000
    
    # Shorter cache for faster development iteration
    CACHE_TIMEOUT = 60


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production logging
    LOG_LEVEL = 'INFO'
    
    # Stricter settings for production
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Production cache settings
    CACHE_TIMEOUT = 600  # 10 minutes
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use in-memory database for testing
    CACHE_TIMEOUT = 0  # No caching during tests


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}