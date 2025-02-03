from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PredictionListCreateView,
    PredictionDetailView,
    DataPointListView,
    InvestmentPreferenceView,
    RiskProfileView,
    NotificationListView,
    EconomicIndicatorListView,
    SectorPerformanceListView,
    GeneratePredictionView,
)

# ===========================
# 1. DRF Router Setup
# ===========================

router = DefaultRouter()
router.register(r'predictions', PredictionListCreateView, basename='prediction')
router.register(r'data-points', DataPointListView, basename='data-point')

# ===========================
# 2. Core URL Patterns
# ===========================

urlpatterns = [
    # Prediction-related URLs
    path('api/v1/predictions/', PredictionListCreateView.as_view(), name='prediction-list-create'),
    path('api/v1/predictions/<int:pk>/', PredictionDetailView.as_view(), name='prediction-detail'),

    # Data Point-related URLs
    path('api/v1/data-points/', DataPointListView.as_view(), name='data-point-list'),

    # User Preference-related URLs
    path('api/v1/user-preferences/', InvestmentPreferenceView.as_view(), name='investment-preference'),

    # Risk Profile-related URLs
    path('api/v1/risk-profile/', RiskProfileView.as_view(), name='risk-profile'),

    # Notification-related URLs
    path('api/v1/notifications/', NotificationListView.as_view(), name='notification-list'),

    # Economic Indicator-related URLs
    path('api/v1/economic-indicators/', EconomicIndicatorListView.as_view(), name='economic-indicator-list'),

    # Sector Performance-related URLs
    path('api/v1/sector-performance/', SectorPerformanceListView.as_view(), name='sector-performance-list'),

    # Custom Prediction Generation Endpoint
    path('api/v1/generate-prediction/', GeneratePredictionView.as_view(), name='generate-prediction'),

    # Include DRF router-generated URLs
    path('api/v1/', include(router.urls)),
]

# ===========================
# 3. Authentication URLs
# ===========================

urlpatterns += [
    # JWT Authentication URLs
    path('api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Additional custom authentication endpoints can be added here
]

# ===========================
# 4. Custom Error Handlers
# ===========================

handler404 = 'investwise.apps.predictor.views.custom_404_handler'
handler500 = 'investwise.apps.predictor.views.custom_500_handler'

# ===========================
# 5. Documentation URLs
# ===========================

urlpatterns += [
    # Swagger/OpenAPI Documentation
    path('api/v1/docs/', include('drf_spectacular.urls')),  # Install drf-spectacular for API docs
]

# ===========================
# 6. Debugging URLs (Optional - For Development Only)
# ===========================

if settings.DEBUG:
    urlpatterns += [
        # Debug Toolbar URLs
        path('__debug__/', include('debug_toolbar.urls')),
    ]
