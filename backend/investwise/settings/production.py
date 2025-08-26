
import os
from .base import *  # Import base settings

# ===========================
# 1. General Settings
# ===========================

DEBUG = False  # Disable debug mode in production

# Get allowed hosts from environment variable
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'investwise.com,www.investwise.com').split(',')

# ===========================
# 2. Security Settings
# ===========================

# Force HTTPS in production
SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
CSRF_COOKIE_SECURE = True  # Ensure CSRF tokens are only sent over HTTPS

# Additional security headers
SECURE_HSTS_SECONDS = 31536000  # Enable HSTS (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Include subdomains in HSTS
SECURE_HSTS_PRELOAD = True  # Allow preloading in browsers

# Cookie security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour session timeout

# Content security
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ===========================
# 3. Database Configuration
# ===========================

# Production should use PostgreSQL via DATABASE_URL environment variable
# This is handled in base.py but we can ensure it's enforced here
if not os.getenv('DJANGO_DATABASE_URL'):
    raise ImproperlyConfigured(
        "DJANGO_DATABASE_URL environment variable is required in production"
    )
# 3. Database Configuration
# ===========================

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DJANGO_DATABASE_URL', 'postgres://user:password@db-production:5432/investwise'),
        conn_max_age=600,
        ssl_require=True  # Enforce SSL for database connections
    )
}

# ===========================
# 4. Caching Configuration
# ===========================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis-production:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# ===========================
# 5. Email Configuration
# ===========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')  # Example: SendGrid
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')  # For SendGrid, use 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_sendgrid_api_key')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@investwise.com')

# ===========================
# 6. Static & Media Files
# ===========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # Optimize static files

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/production.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'predictor': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ===========================
# 8. Celery & Redis Configuration
# ===========================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis-production:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis-production:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ===========================
# 9. Health Check Configuration
# ===========================

HEALTH_CHECK_API_ENDPOINTS = os.getenv('HEALTH_CHECK_API_ENDPOINTS', '').split(',')
HEALTH_CHECK_DATA_SOURCES = json.loads(os.getenv('HEALTH_CHECK_DATA_SOURCES', '[]'))

# ===========================
# 10. CORS Settings
# ===========================

CORS_ALLOW_ALL_ORIGINS = False  # Restrict CORS in production
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# ===========================
# 11. JWT Authentication
# ===========================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Shorter token lifetime for security
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ===========================
# 12. Additional Settings
# ===========================

# Cache timeout for financial data
PREDICTOR_CACHE_TIMEOUT = os.getenv('PREDICTOR_CACHE_TIMEOUT', 3600)  # 1 hour

# AI model path
PREDICTOR_MODEL_PATH = os.getenv('PREDICTOR_MODEL_PATH', BASE_DIR / 'models/predictor_model.h5')

# Data encryption key
DATA_ENCRYPTION_KEY = os.getenv('DATA_ENCRYPTION_KEY', 'production_encryption_key')

# Docker image tag
DOCKER_IMAGE_TAG = os.getenv('DOCKER_IMAGE_TAG', 'production-latest')

# Kubernetes namespace
KUBERNETES_NAMESPACE = os.getenv('KUBERNETES_NAMESPACE', 'production')

# CI/CD pipeline
CI_CD_ENABLED = os.getenv('CI_CD_ENABLED', 'True') == 'True'
CI_CD_GIT_REPO = os.getenv('CI_CD_GIT_REPO', 'https://github.com/username/repo.git')

# ===========================
# 13. Error Handling
# ===========================

# Custom error handling middleware
MIDDLEWARE += ['investwise.middleware.error_handling.CustomErrorHandlerMiddleware']

# ===========================
# 14. Default Primary Key Field Type
# ===========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'