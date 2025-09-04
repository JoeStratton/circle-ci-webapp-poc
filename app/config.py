"""
Configuration for the CircleCI Demo Application

Simple configuration management for the POC.
"""

import os


def get_database_url():
    """Get database URL from environment variables"""
    # Allow override for testing
    if 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    
    # Production: construct from individual environment variables
    db_user = os.environ.get('DB_USERNAME', 'appuser')
    db_password = os.environ.get('DB_PASSWORD', 'defaultpass')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'appdb')
    
    return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Simple configuration dictionary
    config = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'PORT': int(os.environ.get('PORT', 5000)),
        'DEBUG': env == 'development',
        'FLASK_ENV': env
    }
    
    # Set database URL based on environment
    if env == 'development':
        config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    elif env == 'testing':
        config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        config['TESTING'] = True
    else:  # production
        config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    
    return config