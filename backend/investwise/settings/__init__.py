# investwise/settings/__init__.py

# This file makes the 'settings' directory a Python package.
# It dynamically loads the appropriate settings based on the environment.

import os
from pathlib import Path

# Determine the current environment (default to 'local' if not specified).
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local').lower()

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'staging':
    from .staging import *
elif ENVIRONMENT == 'test':
    from .test import *
else:
    from .local import *

# Log the loaded environment (optional)
import logging

logger = logging.getLogger(__name__)
logger.info(f"Loaded settings for {ENVIRONMENT.capitalize()} environment.")

# ===========================
# 1. Environment Configuration
# ===========================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# 2. Application Configuration
# ===========================

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'predictor',  # Add the predictor app to the list of installed apps
]
# Compare this snippet from backend/investwise/settings/test.py:
# from .base import *  # Import base settings
#
# # ===========================
# # 1. General Settings
# # ===========================
#
# DEBUG = False  # Disable debug mode in test environment
#
# investwise/settings/test.py

# This file contains settings specific to the test environment.
# It overrides the base settings for testing purposes.
default_app_config = 'predictor.apps.PredictorConfig'

# ===========================
# 2. Database Configuration
# ===========================

# Use an in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
# Compare this snippet from backend/investwise/settings/production.py:
# from .base import *  # Import base settings
