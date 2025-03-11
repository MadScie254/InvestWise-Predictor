import os
from pathlib import Path
import dj_database_url  # For database URL parsing
import redis  # For Redis integration
from datetime import timedelta
import environ  # Install django-environ for environment variables
from django.core.exceptions import ImproperlyConfigured
from investwise.logging import configure_logging

# ===========================
# 1. Environment Variables
# ===========================

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust for modular settings

# ===========================
# 2. Core Settings
# ===========================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='your_default_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

# Allowed hosts for deployment
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',  # Django REST Framework
    'djoser',  # Authentication utilities
    'django_filters',  # Filtering for DRF
    'drf_spectacular',  # OpenAPI documentation
    'debug_toolbar',  # Debugging tool
    'corsheaders',  # Cross-origin resource sharing
    'celery',  # Background tasks
    'django_celery_results',  # Celery results backend
    'django_celery_beat',  # Periodic tasks
    'health_check',  # Django health checks
    'health_check.db',  # Database backend
    'health_check.cache',  # Cache backend
    'health_check.storage',  # File storage backend

    # Project-specific apps
    'predictor',  # Main app for InvestWise Predictor
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Debug Toolbar
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'investwise.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Template directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'investwise.wsgi.application'
ASGI_APPLICATION = 'investwise.asgi.application'

# ===========================
# 3. Database Configuration
# ===========================

DATABASES = {
    'default': dj_database_url.config(
        default=env('DJANGO_DATABASE_URL', default='postgres://user:password@localhost:5432/investwise'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ===========================
# 4. Health Check Configuration
# ===========================

HEALTH_CHECK_API_ENDPOINTS = env.list('HEALTH_CHECK_API_ENDPOINTS', default=[
    "https://api.example.com/health",
    "https://another-api.com/status",
])

HEALTH_CHECK_DATA_SOURCES = env.json('HEALTH_CHECK_DATA_SOURCES', default=[
    {"url": "https://data-source.com/api", "params": {"key": "value"}},
    {"url": "https://another-data-source.com"},
])

# ===========================
# 0. External Logging Service (Optional)
# ===========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/application.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Initialize custom logging
configure_logging()

# ===========================
# 5. Authentication Configuration
# ===========================

AUTH_USER_MODEL = 'predictor.User'  # Custom user model

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Djoser configuration for JWT-based auth
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {},
}

# ===========================
# 6. Caching Configuration
# ===========================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# ===========================
# 7. Email Configuration
# ===========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='your_email@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='your_email_password')

# ===========================
# 8. Static & Media Files
# ===========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================
# 9. Internationalization
# ===========================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# 10. Security Configuration
# ===========================

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = not DEBUG
X_FRAME_OPTIONS = 'DENY'

# ===========================
# 11. Django REST Framework (DRF) Configuration
# ===========================

REST_FRAMEWORK.update({
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
})

SPECTACULAR_SETTINGS = {
    'TITLE': 'InvestWise Predictor API',
    'DESCRIPTION': 'API documentation for InvestWise Predictor',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'investwise.error_handling.custom_exception_handler',
}

MIDDLEWARE = [
    ...,
    'investwise.error_handling.GlobalErrorHandlerMiddleware',
]

# ===========================
# 12. Celery & Redis Configuration
# ===========================

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ===========================
# 13. Logging Configuration
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
            'filename': BASE_DIR / 'logs/django.log',
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
# 14. Third-Party Integrations
# ===========================

# Tailwind CSS configuration
TAILWIND_APP_NAME = 'theme'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=True if DEBUG else False)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']

# ===========================
# 15. Health Check Settings
# ===========================

# Health check for external APIs
HEALTH_CHECK_API_ENDPOINTS = env.list('HEALTH_CHECK_API_ENDPOINTS', default=[
    "https://api.example.com/health",
    "https://another-api.com/status",
])

# Health check for external data sources
HEALTH_CHECK_DATA_SOURCES = env.json('HEALTH_CHECK_DATA_SOURCES', default=[
    {"url": "https://data-source.com/api", "params": {"key": "value"}},
    {"url": "https://another-data-source.com"},
])

# ===========================
# 16. Security & Deployment
# ===========================

# JWT Authentication
JWT_AUTHENTICATION = {
    'JWT_SECRET_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'JWT_ALGORITHM': 'HS256',
}

# Docker & Kubernetes
DOCKER_IMAGE_TAG = env('DOCKER_IMAGE_TAG', default='latest')
KUBERNETES_NAMESPACE = env('KUBERNETES_NAMESPACE', default='default')

# CI/CD Pipeline
CI_CD_ENABLED = env.bool('CI_CD_ENABLED', default=False)
CI_CD_GIT_REPO = env('CI_CD_GIT_REPO', default='https://github.com/username/repo.git')

# ===========================
# 17. Default Primary Key Field Type
# ===========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===========================
# 18. Additional Settings
# ===========================

# Data Encryption
DATA_ENCRYPTION_KEY = env('DATA_ENCRYPTION_KEY', default='your_encryption_key')

# AI Model Path
PREDICTOR_MODEL_PATH = env('PREDICTOR_MODEL_PATH', default=BASE_DIR / 'models/predictor_model.h5')

# Cache Timeout
PREDICTOR_CACHE_TIMEOUT = env.int('PREDICTOR_CACHE_TIMEOUT', default=3600)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

# ===========================
# 19. Middleware Configuration
# ===========================
MIDDLEWARE = [
    ...,
    'investwise.middleware.RequestLoggingMiddleware',
    'investwise.middleware.UserActivityTrackingMiddleware',
    'investwise.middleware.SecurityHeadersMiddleware',
    'investwise.middleware.APIThrottlingMiddleware',
    'investwise.middleware.MaintenanceModeMiddleware',
    'investwise.middleware.CustomErrorHandlingMiddleware',
]

# ===========================
# 20. Rate Limiting Configuration 
# ===========================
# Rate Limiting Configuration
REDIS_CLIENT = redis.StrictRedis(host='redis', port=6379, db=0)
API_RATE_LIMIT = 100  # Maximum allowed requests per minute
MAINTENANCE_MODE = True

# ===========================
# 21. Custom Permissions Configuration
# ===========================
# Custom Permissions Configuration
# Custom Permissions Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'investwise.permissions.IsInvestor',
    ],
}

# ===========================
# 22. Whitelisted IP Configuration
# ===========================
# Whitelisted IP Configuration
WHITELISTED_IPS = [
    "192.168.1.1",
    "127.0.0.1",
]