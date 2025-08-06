from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API v1 URLs
urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    
    # User Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Predictions
    path('predictions/', views.PredictionListCreateView.as_view(), name='prediction-list'),
    path('predictions/<int:pk>/', views.PredictionDetailView.as_view(), name='prediction-detail'),
    path('predictions/analytics/', views.prediction_analytics, name='prediction-analytics'),
    
    # Investments
    path('investments/', views.InvestmentListCreateView.as_view(), name='investment-list'),
    path('investments/<int:pk>/', views.InvestmentDetailView.as_view(), name='investment-detail'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    
    # Feedback
    path('feedback/', views.FeedbackListCreateView.as_view(), name='feedback-list'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
