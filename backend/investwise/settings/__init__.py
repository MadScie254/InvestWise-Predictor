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

