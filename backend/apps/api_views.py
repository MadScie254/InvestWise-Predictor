from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg, Max, Min, Sum
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)
from .serializers import (
    PredictionSerializer,
    DataPointSerializer,
    InvestmentPreferenceSerializer,
    RiskProfileSerializer,
    NotificationSerializer,
    EconomicIndicatorSerializer,
    SectorPerformanceSerializer,
)
from .utils import generate_prediction


# ===========================
# 1. Batch Prediction API View
# ===========================

class BatchPredictionAPIView(APIView):
    """
    API view for generating multiple predictions in a single request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to generate batch predictions.
        """
        sectors = request.data.get('sectors', [])
        countries = request.data.get('countries', [])

        if not sectors or not countries:
            return Response(
                {"error": "Both sectors and countries are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate input lengths
        if len(sectors) != len(countries):
            return Response(
                {"error": "Sectors and countries must have the same number of elements."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate predictions for each sector-country pair
        predictions = []
        for sector, country in zip(sectors, countries):
            try:
                prediction_data = generate_prediction(sector=sector, country=country)
                prediction = Prediction.objects.create(
                    user=request.user,
                    sector=prediction_data['sector'],
                    country=prediction_data['country'],
                    predicted_value=prediction_data['predicted_value'],
                    status='completed'
                )
                predictions.append(PredictionSerializer(prediction).data)
            except Exception as e:
                return Response(
                    {"error": f"Failed to generate prediction for {sector} ({country}): {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(predictions, status=status.HTTP_201_CREATED)


# ===========================
# 2. Aggregated Data API View
# ===========================

class AggregatedDataAPIView(APIView):
    """
    API view for retrieving aggregated financial data.
    """
    permission_classes = [permissions.AllowAny]  # Public endpoint for demonstration purposes

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve aggregated data.
        """
        indicator = request.query_params.get('indicator')
        country = request.query_params.get('country')

        if not indicator or not country:
            return Response(
                {"error": "Both indicator and country are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch data points for the specified indicator and country
            data_points = DataPoint.objects.filter(indicator=indicator, country=country)

            # Calculate aggregated metrics
            avg_value = data_points.aggregate(Avg('value'))['value__avg']
            max_value = data_points.aggregate(Max('value'))['value__max']
            min_value = data_points.aggregate(Min('value'))['value__min']
            total_value = data_points.aggregate(Sum('value'))['value__sum']

            # Prepare response data
            response_data = {
                "indicator": indicator,
                "country": country,
                "average_value": round(avg_value, 2) if avg_value else None,
                "maximum_value": round(max_value, 2) if max_value else None,
                "minimum_value": round(min_value, 2) if min_value else None,
                "total_value": round(total_value, 2) if total_value else None,
                "timestamp": timezone.now().isoformat(),
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve aggregated data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ===========================
# 3. Trend Analysis API View
# ===========================

class TrendAnalysisAPIView(APIView):
    """
    API view for analyzing trends in sector performance.
    """
    permission_classes = [permissions.AllowAny]  # Public endpoint for demonstration purposes

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to analyze sector performance trends.
        """
        sector = request.query_params.get('sector')
        start_year = request.query_params.get('start_year')
        end_year = request.query_params.get('end_year')

        if not sector or not start_year or not end_year:
            return Response(
                {"error": "Sector, start_year, and end_year are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch sector performance data within the specified range
            performances = SectorPerformance.objects.filter(
                sector=sector,
                year__gte=start_year,
                year__lte=end_year
            ).order_by('year')

            # Prepare response data
            response_data = [
                {
                    "year": perf.year,
                    "growth_rate": perf.growth_rate,
                    "market_size": perf.market_size,
                }
                for perf in performances
            ]

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to analyze trends: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ===========================
# 4. Custom Pagination Class
# ===========================

class LargeResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for large result sets.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# ===========================
# 5. Historical Data API View
# ===========================

class HistoricalDataAPIView(APIView):
    """
    API view for retrieving historical financial data.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve historical data.
        """
        indicator = request.query_params.get('indicator')
        country = request.query_params.get('country')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not indicator or not country or not start_date or not end_date:
            return Response(
                {"error": "Indicator, country, start_date, and end_date are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch historical data points
            data_points = DataPoint.objects.filter(
                indicator=indicator,
                country=country,
                date__range=[start_date, end_date]
            ).order_by('date')

            # Paginate results
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(data_points, request)
            serializer = DataPointSerializer(paginated_data, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve historical data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
