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
