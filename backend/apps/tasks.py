from celery import shared_task
from .utils import fetch_financial_data_from_api, train_neural_network

@shared_task
def fetch_financial_data():
    """
    Fetches financial data from external APIs and stores it in the database.
    """
    data = fetch_financial_data_from_api()
    # Process and save data to the database
    print("Fetched financial data:", data)

@shared_task
def train_ai_model():
    """
    Trains the AI model using historical financial data.
    """
    train_neural_network()
    print("AI model training completed.")