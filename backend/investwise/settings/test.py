from .base import *  # Import base settings

# ===========================
# 1. General Settings
# ===========================

DEBUG = False  # Disable debug mode during testing

ALLOWED_HOSTS = ['testserver']  # Allow only the test server host

# ===========================
# 2. Database Configuration
# ===========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Use SQLite for faster tests
        'NAME': ':memory:',  # In-memory database for isolation
    }
}

# ===========================
# 3. Caching Configuration
# ===========================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # Disable caching during tests
    }
}

# ===========================
# 4. Email Configuration
# ===========================

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'  # Store emails in memory

# ===========================
# 5. Static & Media Files
# ===========================

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Disable static file handling during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ===========================
# 6. Logging Configuration
# ===========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',  # Log only errors during tests
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'predictor': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ===========================
# 7. Middleware Configuration
# ===========================

# Disable unnecessary middleware during tests
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ===========================
# 8. Celery & Redis Configuration
# ===========================

CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously during tests
CELERY_TASK_EAGER_PROPAGATES = True  # Propagate exceptions in tasks

# ===========================
# 9. Testing-Specific Settings
# ===========================

# Disable password validation during tests
AUTH_PASSWORD_VALIDATORS = []

# Disable CSRF checks during tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# ===========================
# 10. Additional Settings
# ===========================

# Cache timeout for financial data
PREDICTOR_CACHE_TIMEOUT = 0  # Disable caching during tests

# AI model path
PREDICTOR_MODEL_PATH = BASE_DIR / 'models/predictor_model_test.h5'  # Use a test-specific model

# Data encryption key
DATA_ENCRYPTION_KEY = 'test_encryption_key'

# Docker image tag
DOCKER_IMAGE_TAG = 'test-latest'

# Kubernetes namespace
KUBERNETES_NAMESPACE = 'test'

# CI/CD pipeline
CI_CD_ENABLED = False  # Disable CI/CD during tests
CI_CD_GIT_REPO = ''

# ===========================
# 11. Default Primary Key Field Type
# ===========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
