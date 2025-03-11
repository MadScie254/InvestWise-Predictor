import os
import json
import logging
import requests
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.utils.timezone import now
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model  # Install TensorFlow for neural networks
import numpy as np


# ===========================
# 1. Logging Configuration
# ===========================

logger = logging.getLogger(__name__)


# ===========================
# 2. Data Processing Utilities
# ===========================

def fetch_financial_data(source: str, params: dict = None):
    """
    Fetches financial data from external APIs or local sources.
    Caches the results to improve performance.

    Args:
        source (str): The API endpoint or data source URL.
        params (dict, optional): Query parameters for the API request.

    Returns:
        dict: Parsed JSON response from the data source.
    """
    cache_key = f"financial_data_{source}_{json.dumps(params)}"
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.info(f"Using cached data for {source}.")
        return cached_data

    try:
        response = requests.get(source, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the data for future use
        cache.set(cache_key, data, timeout=settings.PREDICTOR_CACHE_TIMEOUT)
        logger.info(f"Fetched and cached data from {source}.")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from {source}: {e}")
        raise


def preprocess_data(data: list) -> np.ndarray:
    """
    Preprocesses raw financial data for AI model input.

    Args:
        data (list): List of raw data points.

    Returns:
        np.ndarray: Processed data ready for prediction.
    """
    scaler = StandardScaler()
    processed_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
    return processed_data


# ===========================
# 3. AI Model Integration Utilities
# ===========================

def load_model(model_path: str):
    """
    Loads a pre-trained AI model from the specified path.

    Args:
        model_path (str): Path to the model file.

    Returns:
        object: Loaded AI model instance.
    """
    if not os.path.exists(model_path):
        logger.error(f"Model file not found at {model_path}.")
        return None

    try:
        model = load_model(model_path)
        logger.info("AI model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to load AI model: {e}")
        return None


def generate_prediction(sector: str, country: str) -> dict:
    """
    Generates an investment prediction using the AI model.

    Args:
        sector (str): The industry or sector being analyzed.
        country (str): The country or region for the prediction.

    Returns:
        dict: Prediction results including predicted value and metadata.
    """
    # Step 1: Fetch relevant data for the sector and country
    data_source = settings.PREDICTOR_DATA_SOURCES.get(country, {}).get(sector)
    if not data_source:
        logger.warning(f"No data source found for {sector} in {country}.")
        return {}

    try:
        raw_data = fetch_financial_data(data_source['url'], params=data_source.get('params', {}))
        processed_data = preprocess_data(raw_data['values'])

        # Step 2: Load the AI model
        model = load_model(settings.PREDICTOR_MODEL_PATH)
        if not model:
            logger.error("AI model could not be loaded.")
            return {}

        # Step 3: Generate prediction
        prediction = model.predict(processed_data)[-1][0]
        return {
            "sector": sector,
            "country": country,
            "predicted_value": round(float(prediction), 2),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to generate prediction: {e}")
        return {}


# ===========================
# 4. Financial Calculation Utilities
# ===========================

def calculate_return_on_investment(initial_investment: float, final_value: float) -> float:
    """
    Calculates the return on investment (ROI) percentage.

    Args:
        initial_investment (float): Initial investment amount.
        final_value (float): Final value of the investment.

    Returns:
        float: ROI percentage.
    """
    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive.")
    roi = ((final_value - initial_investment) / initial_investment) * 100
    return round(roi, 2)


def calculate_compound_interest(principal: float, rate: float, time_years: float) -> float:
    """
    Calculates compound interest.

    Args:
        principal (float): Principal amount.
        rate (float): Annual interest rate (in decimal form).
        time_years (float): Time period in years.

    Returns:
        float: Total amount after compound interest.
    """
    if principal <= 0 or rate < 0 or time_years < 0:
        raise ValueError("Invalid input values.")
    total_amount = principal * (1 + rate) ** time_years
    return round(total_amount, 2)


# ===========================
# 5. Date and Time Utilities
# ===========================

def get_current_date():
    """
    Gets the current date in ISO format.

    Returns:
        str: Current date in ISO format.
    """
    return now().date().isoformat()


def get_date_range(start_date: str, end_date: str) -> list:
    """
    Generates a list of dates between start_date and end_date.

    Args:
        start_date (str): Start date in ISO format.
        end_date (str): End date in ISO format.

    Returns:
        list: List of dates in ISO format.
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    delta = end - start
    return [(start + timedelta(days=i)).date().isoformat() for i in range(delta.days + 1)]


# ===========================
# 6. Error Handling Utilities
# ===========================

def handle_api_error(response: requests.Response):
    """
    Handles errors from API responses.

    Args:
        response (requests.Response): API response object.

    Raises:
        ValueError: If the API response indicates an error.
    """
    if response.status_code != 200:
        error_message = response.json().get('error', 'Unknown error')
        logger.error(f"API error: {error_message}")
        raise ValueError(error_message)


# ===========================
# 7. Caching Utilities
# ===========================

def cache_data(key: str, data: dict, timeout: int = None):
    """
    Caches data with a specified timeout.

    Args:
        key (str): Cache key.
        data (dict): Data to cache.
        timeout (int, optional): Timeout in seconds. Defaults to settings.PREDICTOR_CACHE_TIMEOUT.
    """
    timeout = timeout or settings.PREDICTOR_CACHE_TIMEOUT
    cache.set(key, data, timeout=timeout)
    logger.info(f"Cached data with key: {key}")


def get_cached_data(key: str):
    """
    Retrieves cached data by key.

    Args:
        key (str): Cache key.

    Returns:
        dict: Cached data or None if not found.
    """
    data = cache.get(key)
    if data:
        logger.info(f"Retrieved cached data with key: {key}")
    else:
        logger.info(f"No cached data found for key: {key}")
    return data


# ===========================
# 8. Notification Utilities
# ===========================

def send_notification(user_id: int, message: str):
    """
    Sends a notification to the specified user.

    Args:
        user_id (int): ID of the user to notify.
        message (str): Notification message.
    """
    from .models import Notification

    try:
        notification = Notification.objects.create(user_id=user_id, message=message)
        logger.info(f"Notification sent to user {user_id}: {message}")
        return notification.id
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return None

def fetch_financial_data_from_api():
    """
    Simulates fetching financial data from an external API.
    Replace with actual API calls in production.
    """
    return {"data": "Sample financial data"}

def train_neural_network():
    """
    Simulates training a neural network.
    Replace with actual AI model training logic in production.
    """
    print("Training neural network...")

def send_mail(subject, message, from_email, recipient_list, fail_silently):
    """
    Simulates sending an email.
    Replace with actual email sending logic in production.
    """
    print(f"Sending email to {recipient_list}: {subject}\n{message}")
#     pass

def get_from_cache(cache_key):
    """
    Simulates getting data from a cache.
    Replace with actual cache retrieval logic in production.
    """
    print(f"Getting data from cache: {cache_key}")
    return None

def set_to_cache(cache_key, data, timeout):
    """
    Simulates setting data in a cache.
    Replace with actual cache setting logic in production.
    """
    print(f"Setting data in cache: {cache_key}")
    pass

def delete_from_cache(cache_key):
    """
    Simulates deleting data from a cache.
    Replace with actual cache deletion logic in production.
    """
    print(f"Deleting data from cache: {cache_key}")
    pass


def log_cache_usage(action, key, result=None):
    """
    Log cache usage for monitoring and debugging.
    """
    print(f"Cache {action}: {key}")
    if result is not None:
        print(f"Cache {action} result: {result}")
#     pass

def configure_logging():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if getattr(settings, 'LOGGING_EXTERNAL_SERVICE', False):
        try:
            from .external_logging import ExternalLogHandler
            external_handler = ExternalLogHandler()
            external_handler.setLevel(logging.WARNING)  # Log WARNING and above to external service
            external_handler.setFormatter(formatter)
            logger.addHandler(external_handler)
        except ImportError:
            logger.warning("External logging service is not available.")

    return logger

def fetch_financial_data_from_api():
    """
    Simulates fetching financial data from an external API.
    Replace with actual API calls in production.
    """
    return [
        {"sector": "Technology", "country": "USA", "indicator": "GDP", "value": random.uniform(100, 200)},
        {"sector": "Agriculture", "country": "Kenya", "indicator": "Inflation", "value": random.uniform(5, 10)},
    ]

def train_neural_network():
    """
    Simulates training a neural network.
    Replace with actual AI model training logic in production.
    """
    print("Training neural network...")

