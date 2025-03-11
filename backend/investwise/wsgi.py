import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise  # For serving static files in production

# ===========================
# 1. Environment Configuration
# ===========================

# Set the default Django settings module for the WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investwise.settings.production')

# ===========================
# 2. Initialize WSGI Application
# ===========================

# Get the Django WSGI application
application = get_wsgi_application()

# ===========================
# 3. Static Files Middleware
# ===========================

# Use WhiteNoise to serve static files efficiently in production
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))

# ===========================
# 4. Logging Configuration
# ===========================

import logging

logger = logging.getLogger(__name__)
logger.info("WSGI application initialized with WhiteNoise for static files.")

# ===========================
# 5. Optional: Health Check Endpoint
# ===========================

# Add a simple health check endpoint for monitoring
def health_check(environ, start_response):
    """
    A simple health check endpoint to verify the application is running.
    Returns a 200 OK response with a plain text message.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b"OK"]

# Mount the health check endpoint at /health/
from wsgiref.util import shift_path_info

def application_with_health_check(environ, start_response):
    """
    Wraps the main WSGI application to include a health check endpoint.
    """
    if environ.get('PATH_INFO', '').strip('/') == 'health':
        return health_check(environ, start_response)
    return application(environ, start_response)

# Replace the default application with the health check wrapper
application = application_with_health_check
