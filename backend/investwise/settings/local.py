
from .base import *  # Import base settings

# ===========================
# 1. General Settings
# ===========================

DEBUG = True  # Enable debug mode for local development

ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Allow local hosts only

# ===========================
# 2. Security Settings
# ===========================

# Disable strict security settings in local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# ===========================
# 3. Database Configuration
# ===========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'investwise_local'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ===========================
# 4. Caching Configuration
# ===========================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ===========================
# 5. Email Configuration
# ===========================

# Use console backend for email during local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===========================
# 6. Static & Media Files
# ===========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================
# 7. Logging Configuration
# ===========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/local.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'predictor': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# ===========================
# 8. Celery & Redis Configuration
# ===========================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ===========================
# 9. CORS Settings
# ===========================

CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins in local development

# ===========================
# 10. JWT Authentication
# ===========================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Longer token lifetime for local development
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ===========================
# 11. Additional Settings
# ===========================

# Cache timeout for financial data
PREDICTOR_CACHE_TIMEOUT = os.getenv('PREDICTOR_CACHE_TIMEOUT', 3600)  # 1 hour

# AI model path
PREDICTOR_MODEL_PATH = os.getenv('PREDICTOR_MODEL_PATH', BASE_DIR / 'models/predictor_model.h5')

# Data encryption key
DATA_ENCRYPTION_KEY = os.getenv('DATA_ENCRYPTION_KEY', 'local_encryption_key')

# Docker image tag
DOCKER_IMAGE_TAG = os.getenv('DOCKER_IMAGE_TAG', 'local-latest')

# Kubernetes namespace
KUBERNETES_NAMESPACE = os.getenv('KUBERNETES_NAMESPACE', 'local')

# CI/CD pipeline
CI_CD_ENABLED = os.getenv('CI_CD_ENABLED', 'False') == 'True'
CI_CD_GIT_REPO = os.getenv('CI_CD_GIT_REPO', 'https://github.com/username/repo.git')

# ===========================
# 12. Debug Toolbar Configuration
# ===========================

INSTALLED_APPS += ['debug_toolbar']  # Add Debug Toolbar
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # Insert Debug Toolbar middleware

INTERNAL_IPS = ['127.0.0.1']  # Required for Debug Toolbar

# ===========================
# 13. Environment Variables
# ===========================

# Load environment variables from .env file
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()

# ===========================
# 14. Default Primary Key Field Type
# ===========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'