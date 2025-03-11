from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from predictor.views import (
    PredictionViewSet,
    UserRegistrationView,
    UserLoginView,
    DashboardView,
    NotificationViewSet,
)

# ===========================
# 1. API Routes
# ===========================

api_patterns = [
    # Authentication Endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User Registration and Login
    path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('auth/login/', UserLoginView.as_view(), name='user_login'),

    # Prediction Endpoints
    path('predictions/', PredictionViewSet.as_view({'get': 'list', 'post': 'create'}), name='prediction_list_create'),
    path('predictions/<int:pk>/', PredictionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='prediction_detail'),

    # Notifications Endpoints
    path('notifications/', NotificationViewSet.as_view({'get': 'list'}), name='notification_list'),
    path('notifications/<int:pk>/', NotificationViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='notification_detail'),

    # Dashboard Endpoint
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

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
