import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from predictor import routing as predictor_routing  # Import WebSocket routing from the predictor app

# ===========================
# 1. Environment Configuration
# ===========================

# Set the default Django settings module for ASGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investwise.settings')

# ===========================
# 2. Application Initialization
# ===========================

# Initialize the Django ASGI application
django_asgi_app = get_asgi_application()

# ===========================
# 3. ASGI Application Configuration
# ===========================

# Define the ASGI application using ProtocolTypeRouter
application = ProtocolTypeRouter({
    # HTTP requests are handled by the Django ASGI application
    "http": django_asgi_app,

    # WebSocket connections are routed through AuthMiddlewareStack and URLRouter
    "websocket": AuthMiddlewareStack(
        URLRouter(
            predictor_routing.websocket_urlpatterns  # Include WebSocket routes from the predictor app
        )
    ),
})

# ===========================
# 4. Logging Configuration
# ===========================

# Add logging to monitor ASGI-related events
import logging

logger = logging.getLogger(__name__)
logger.info("ASGI application initialized with WebSocket support.")

# ===========================
# 5. Additional Notes
# ===========================
#
# The ASGI application configuration in this file is similar to the WSGI application configuration in the `wsgi.py` file.
# The key difference is the use of the `ProtocolTypeRouter` to handle different types of connections (HTTP and WebSocket).
# The `AuthMiddlewareStack` is used to add authentication support for WebSocket connections.
# The `URLRouter` is used to route WebSocket connections to the appropriate consumer based on the URL path.
# The `predictor_routing.websocket_urlpatterns` includes the WebSocket URL patterns defined in the `routing.py` file of the predictor app.
# The logging configuration at the end of the file adds a log message to indicate that the ASGI application has been initialized.
# This logging message can be useful for monitoring and debugging ASGI-related events.
# You can customize the logging configuration based on your specific requirements and preferences.
# For more information on ASGI, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/
# For more information on logging in Django, refer to the Django documentation: https://docs.djangoproject.com/en/stable/topics/logging/
# For more information on ASGI application configuration, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/glossary.html#term-application
# For more information on WebSocket routing in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/routing.html#routing
# For more information on the ProtocolTypeRouter in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/routing.html#protocoltyperouter
# For more information on the AuthMiddlewareStack in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/authentication.html#authmiddlewarestack
# For more information on the URLRouter in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/routing.html#urlrouter
# For more information on ASGI application initialization, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/routing.html#application
# For more information on ASGI application configuration in Django, refer to the Django documentation: https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
# For more information on logging in Python, refer to the Python documentation: https://docs.python.org/3/library/logging.html
# For more information on logging configuration in Django, refer to the Django documentation: https://docs.djangoproject.com/en/stable/topics/logging/
# For more information on logging best practices, refer to the Python logging cookbook: https://docs.python.org/3/howto/logging.html#logging-cookbook
# For more information on monitoring and debugging ASGI applications, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/debugging.html
# For more information on WebSocket support in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/websockets.html
# For more information on WebSocket consumers in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/consumers.html
# For more information on WebSocket URL routing in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/routing.html#routing
# For more information on WebSocket connections in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/websockets.html
# For more information on WebSocket protocol support in Django Channels, refer to the Django Channels documentation: https://channels.readthedocs.io/en/stable/topics/websockets.html#protocol-support
