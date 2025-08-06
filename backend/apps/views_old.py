from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Prediction, Notification
from .serializers import PredictionSerializer, NotificationSerializer
from .permissions import IsOwnerOrAdmin
from .models import (
    User,
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)
from .serializers import (
    UserSerializer,
    PredictionSerializer,
    DataPointSerializer,
    InvestmentPreferenceSerializer,
    RiskProfileSerializer,
    NotificationSerializer,
    EconomicIndicatorSerializer,
    SectorPerformanceSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .utils import generate_prediction


# ===========================
# 1. Custom Pagination Class
# ===========================

class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API views.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===========================
# 2. Core API Views
# ===========================

class PredictionListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating predictions.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['sector', 'country']
    filterset_fields = ['status', 'created_at']

    def perform_create(self, serializer):
        """
        Save the prediction with the currently authenticated user.
        """
        try:
            # Generate prediction using AI model
            prediction_data = generate_prediction(
                sector=self.request.data.get('sector'),
                country=self.request.data.get('country')
            )
            serializer.save(user=self.request.user, **prediction_data)
        except Exception as e:
            raise ValidationError(f"Failed to generate prediction: {e}")

    def get_queryset(self):
        """
        Customize the queryset to include only predictions for the current user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-created_at')


class PredictionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific prediction.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """
        Retrieve the prediction object and ensure it belongs to the current user.
        """
        obj = get_object_or_404(self.queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj


class DataPointListView(generics.ListAPIView):
    """
    API view for listing all data points.
    """
    queryset = DataPoint.objects.all()
    serializer_class = DataPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['indicator', 'country']
    filterset_fields = ['date', 'source']


class InvestmentPreferenceView(generics.RetrieveUpdateAPIView):
    """
    API view for managing investment preferences of the current user.
    """
    queryset = InvestmentPreference.objects.all()
    serializer_class = InvestmentPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve or create the investment preference for the current user.
        """
        obj, created = InvestmentPreference.objects.get_or_create(user=self.request.user)
        return obj


class RiskProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving the risk profile of the current user.
    """
    queryset = RiskProfile.objects.all()
    serializer_class = RiskProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve the risk profile for the current user.
        """
        obj, created = RiskProfile.objects.get_or_create(user=self.request.user)
        return obj


class NotificationListView(generics.ListAPIView):
    """
    API view for listing all notifications for the current user.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Customize the queryset to include only notifications for the current user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-created_at')


# ===========================
# 3. Supporting API Views
# ===========================

class EconomicIndicatorListView(generics.ListAPIView):
    """
    API view for listing all economic indicators.
    """
    queryset = EconomicIndicator.objects.all()
    serializer_class = EconomicIndicatorSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class SectorPerformanceListView(generics.ListAPIView):
    """
    API view for listing sector performance data.
    """
    queryset = SectorPerformance.objects.all()
    serializer_class = SectorPerformanceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['sector']
    filterset_fields = ['year']


# ===========================
# 4. Custom Function-Based Views
# ===========================

class GeneratePredictionView(APIView):
    """
    Custom API view for generating predictions based on user input.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to generate predictions.
        """
        sector = request.data.get('sector')
        country = request.data.get('country')

        if not sector or not country:
            return Response({"error": "Sector and country are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate prediction using AI model
            prediction_data = generate_prediction(sector=sector, country=country)

            # Save the prediction to the database
            prediction = Prediction.objects.create(
                user=request.user,
                sector=prediction_data['sector'],
                country=prediction_data['country'],
                predicted_value=prediction_data['predicted_value'],
                status='completed'
            )

            # Serialize and return the response
            serializer = PredictionSerializer(prediction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Failed to generate prediction: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===========================
# 5. Utility Functions
# ===========================

def generate_prediction(sector, country):
    """
    Utility function to generate predictions using the AI model.
    Simulates the process of generating predictions for demonstration purposes.
    """
    from random import uniform

    # Simulate AI-generated prediction (replace this with actual AI logic)
    predicted_value = round(uniform(100, 1000), 2)

    return {
        "sector": sector,
        "country": country,
        "predicted_value": predicted_value,
    }


# ===========================
# 6. ViewSets
# ===========================
class PredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing predictions.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """
        Associate the prediction with the current user upon creation.
        """
        serializer.save(owner=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter notifications for the current user.
        """
        return self.queryset.filter(user=self.request.user)
    
# ===========================
# 7. User Authentication Views
# ===========================

class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    """
    def post(self, request):
        # Logic for user registration
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    """
    def post(self, request):
        # Logic for user login
        return Response({"message": "User logged in successfully."}, status=status.HTTP_200_OK)


class DashboardView(APIView):
    """
    API endpoint for the user dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch aggregated data for the dashboard
        data = {
            "total_predictions": Prediction.objects.filter(owner=request.user).count(),
            "unread_notifications": Notification.objects.filter(user=request.user, is_read=False).count(),
        }
        return Response(data, status=status.HTTP_200_OK)