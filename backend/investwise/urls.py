from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Try to import JWT views, skip if not available
try:
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
        TokenVerifyView,
    )
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# ===========================
# 1. API Routes
# ===========================

api_patterns = [
    # App API endpoints
    path('v1/', include('apps.urls')),
]

# Add JWT endpoints if available
if JWT_AVAILABLE:
    api_patterns.extend([
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])

# ===========================
# 2. Main URL Configuration
# ===========================

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),

    # API Routes
    path('api/v1/', include(api_patterns)),

    # Health Check Endpoint (Optional)
    path('health/', include('health_check.urls')),

    # Swagger/OpenAPI Documentation (Optional)
    path('docs/', include('drf_spectacular.urls')),
]

# ===========================
# 3. Serve Static and Media Files in Development
# ===========================

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
