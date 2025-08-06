# investwise/settings/__init__.py

# This file makes the 'settings' directory a Python package.
# It dynamically loads the appropriate settings based on the environment.

import os
from pathlib import Path

# Determine the current environment (default to 'local' if not specified).
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local').lower()

# Map environments to their corresponding settings files.
settings_files = {
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
settings_file = settings_files.get(ENVIRONMENT, 'settings')

try:
    # Import the appropriate settings module
    if settings_file == 'settings':
        from .settings import *
    elif settings_file == 'local':
        from .local import *
    elif settings_file == 'test':
        from .test import *
    elif settings_file == 'production':
        from .production import *
    elif settings_file == 'staging':
        from .staging import *
    else:
        from .settings import *  # fallback to main settings
        
except ImportError as e:
    # Fallback to main settings if specific environment settings don't exist
    from .settings import *
