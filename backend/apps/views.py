from typing import Optional, Dict, Any
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

# Try to import JWT tokens, skip if not available
try:
    from rest_framework_simplejwt.tokens import RefreshToken
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    RefreshToken = None

from .models import Prediction, Investment, Notification, Feedback
from .serializers import (
    UserSerializer, PredictionSerializer, InvestmentSerializer,
    NotificationSerializer, FeedbackSerializer, UserRegistrationSerializer
)
from .utils import generate_prediction


def create_jwt_response(user) -> Dict[str, Any]:
    """Create JWT token response for user authentication."""
    if JWT_AVAILABLE and RefreshToken:
        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    else:
        return {
            'user': UserSerializer(user).data,
            'message': 'Authentication successful. JWT tokens are not available - please install djangorestframework-simplejwt.',
            'jwt_available': False
        }


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a new user and return authentication tokens."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_data = create_jwt_response(user)
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """Login user and return authentication tokens."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        response_data = create_jwt_response(user)
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """Logout user by blacklisting refresh token."""
    if not JWT_AVAILABLE:
        return Response({
            'message': 'Logged out successfully. JWT tokens are not available.',
            'jwt_available': False
        })
    
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    """User profile management"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PredictionListCreateView(generics.ListCreateAPIView):
    """List user predictions or create new prediction"""
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        prediction = serializer.save(user=self.request.user)
        # Generate prediction asynchronously (in a real app, use Celery)
        prediction_result = generate_prediction(
            prediction.symbol,
            prediction.prediction_type,
            prediction.time_horizon
        )
        prediction.predicted_value = prediction_result.get('predicted_value', 0)
        prediction.confidence = prediction_result.get('confidence', 0)
        prediction.status = 'completed'
        prediction.save()


class PredictionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a prediction"""
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def prediction_analytics(request):
    """Get prediction analytics and statistics"""
    predictions = Prediction.objects.filter(user=request.user)
    
    analytics = {
        'total_predictions': predictions.count(),
        'completed_predictions': predictions.filter(status='completed').count(),
        'pending_predictions': predictions.filter(status='pending').count(),
        'average_confidence': predictions.filter(status='completed').aggregate(
            avg_confidence=Avg('confidence')
        )['avg_confidence'] or 0,
        'prediction_types': {
            'price': predictions.filter(prediction_type='price').count(),
            'trend': predictions.filter(prediction_type='trend').count(),
            'volatility': predictions.filter(prediction_type='volatility').count(),
            'risk': predictions.filter(prediction_type='risk').count(),
        },
        'recent_accuracy': 85.2,  # Mock data - would calculate from actual results
        'monthly_predictions': predictions.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count(),
    }
    
    return Response(analytics)


class InvestmentListCreateView(generics.ListCreateAPIView):
    """List user investments or add new investment"""
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvestmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an investment"""
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)


class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a notification"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({'message': 'All notifications marked as read'})


class FeedbackListCreateView(generics.ListCreateAPIView):
    """List user feedback or submit new feedback"""
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    
    stats = {
        'total_predictions': Prediction.objects.filter(user=user).count(),
        'total_investments': Investment.objects.filter(user=user).count(),
        'unread_notifications': Notification.objects.filter(user=user, read=False).count(),
        'recent_predictions': PredictionSerializer(
            Prediction.objects.filter(user=user).order_by('-created_at')[:5],
            many=True
        ).data,
        'portfolio_value': sum([
            float(inv.shares) * float(inv.purchase_price) 
            for inv in Investment.objects.filter(user=user)
        ]),
        'prediction_accuracy': 84.5,  # Mock data
        'active_alerts': 3,  # Mock data
    }
    
    return Response(stats)
