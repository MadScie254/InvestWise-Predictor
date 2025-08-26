# investwise/settings/__init__.py

"""
Dynamic settings loader for InvestWise Predictor.

This module automatically loads the appropriate settings based on the DJANGO_ENV 
environment variable. It provides a secure, environment-driven configuration system.

Environment Variables:
    DJANGO_ENV: Determines which settings file to load
        - 'local', 'dev', 'development' -> local.py
        - 'test', 'testing' -> test.py  
        - 'staging' -> staging.py
        - 'prod', 'production' -> production.py
        - Default: base.py

Usage:
    export DJANGO_ENV=production
    python manage.py runserver --settings=investwise.settings
"""

import os
import logging

# Set up logging for settings loading
logger = logging.getLogger(__name__)

# Determine the current environment (default to 'local' if not specified).
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local').lower()

# Map environments to their corresponding settings files.
SETTINGS_MAP = {
    'local': 'local',
    'dev': 'local', 
    'development': 'local',
    'test': 'test',
    'testing': 'test',
    'prod': 'production',
    'production': 'production',
    'staging': 'staging',
}

# Get the settings file for the current environment.
settings_module = SETTINGS_MAP.get(ENVIRONMENT, 'base')

try:
    # Import the appropriate settings module
    if settings_module == 'local':
        from .local import *
        logger.info("Loaded LOCAL settings")
    elif settings_module == 'test':
        from .test import *
        logger.info("Loaded TEST settings")
    elif settings_module == 'production':
        from .production import *
        logger.info("Loaded PRODUCTION settings")
    elif settings_module == 'staging':
        from .staging import *
        logger.info("Loaded STAGING settings")
    else:
        from .base import *
        logger.info("Loaded BASE settings")
        
except ImportError as e:
    # Fallback to base settings if specific environment settings don't exist
    from .base import *
    logger.warning(f"Failed to load {settings_module} settings, falling back to base: {e}")

# Log the current configuration for debugging
logger.info(f"Django environment: {ENVIRONMENT}")
logger.info(f"Settings module: {settings_module}")
logger.info(f"Debug mode: {DEBUG}")
logger.info(f"Allowed hosts: {ALLOWED_HOSTS}")
