"""
Prefect flows for ML pipeline orchestration
"""
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import subprocess
import sys
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def check_data_availability() -> bool:
    """Check if training data is available"""
    data_path = "data/processed/combined_features.csv"
    
    if not os.path.exists(data_path):
        logger.error(f"Training data not found at {data_path}")
        return False
    
    # Check if data file is not empty
    file_size = os.path.getsize(data_path)
    if file_size == 0:
        logger.error("Training data file is empty")
        return False
    
    logger.info(f"Training data available: {data_path} ({file_size} bytes)")
    return True

@task
def generate_sample_data() -> bool:
    """Generate sample data if not available"""
    try:
        result = subprocess.run([
            sys.executable, "scripts/generate_sample_data.py"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("Sample data generated successfully")
            return True
        else:
            logger.error(f"Sample data generation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Sample data generation timed out")
        return False
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        return False

@task
def run_training() -> Dict[str, Any]:
    """Run ML model training"""
    try:
        # Run the training script
        result = subprocess.run([
            sys.executable, "ml/training/train.py",
            "--data-path", "data/processed/combined_features.csv"
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            logger.info("Training completed successfully")
            logger.info(f"Training output: {result.stdout}")
            
            return {
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            logger.error(f"Training failed: {result.stderr}")
            return {
                "status": "failed",
                "output": result.stdout,
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Training timed out")
        return {
            "status": "timeout",
            "output": None,
            "error": "Training process timed out"
        }
    except Exception as e:
        logger.error(f"Error running training: {e}")
        return {
            "status": "error",
            "output": None,
            "error": str(e)
        }

@task
def validate_model() -> bool:
    """Validate the trained model"""
    try:
        # Check if model artifacts exist
        model_dir = "ml/training/artifacts"
        
        if not os.path.exists(model_dir):
            logger.error("Model artifacts directory not found")
            return False
        
        # Check for model files
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]
        
        if not model_files:
            logger.error("No model files found in artifacts directory")
            return False
        
        logger.info(f"Found model files: {model_files}")
        
        # TODO: Add model validation logic (load model, test predictions, etc.)
        
        return True
        
    except Exception as e:
        logger.error(f"Model validation error: {e}")
        return False

@task
def send_notification(status: str, details: str = None) -> None:
    """Send training completion notification"""
    # In production, this would send emails, Slack messages, etc.
    message = f"ML Training {status.upper()}"
    if details:
        message += f": {details}"
    
    logger.info(f"NOTIFICATION: {message}")
    
    # Write to a file that could be monitored
    notification_file = "logs/training_notifications.log"
    os.makedirs(os.path.dirname(notification_file), exist_ok=True)
    
    with open(notification_file, "a") as f:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        f.write(f"{timestamp} - {message}\n")

@flow(name="ml-training-pipeline")
def training_flow() -> str:
    """
    Main training pipeline flow
    """
    logger.info("Starting ML training pipeline")
    
    try:
        # Check if data is available
        data_available = check_data_availability()
        
        if not data_available:
            logger.info("Training data not available, generating sample data")
            data_generated = generate_sample_data()
            
            if not data_generated:
                send_notification("FAILED", "Could not generate training data")
                return "FAILED"
        
        # Run training
        logger.info("Starting model training")
        training_result = run_training()
        
        if training_result["status"] != "success":
            send_notification("FAILED", f"Training failed: {training_result['error']}")
            return "FAILED"
        
        # Validate model
        logger.info("Validating trained model")
        model_valid = validate_model()
        
        if not model_valid:
            send_notification("FAILED", "Model validation failed")
            return "FAILED"
        
        # Success
        send_notification("SUCCESS", "Training completed successfully")
        logger.info("ML training pipeline completed successfully")
        return "SUCCESS"
        
    except Exception as e:
        logger.error(f"Training pipeline error: {e}")
        send_notification("ERROR", f"Pipeline error: {str(e)}")
        return "ERROR"

@flow(name="model-retraining-schedule")
def scheduled_retraining_flow():
    """
    Scheduled retraining flow (to be run weekly/monthly)
    """
    logger.info("Starting scheduled model retraining")
    
    # Check if retraining is needed (based on performance metrics, data drift, etc.)
    # This is a simplified version - in production you'd check model performance
    
    result = training_flow()
    
    if result == "SUCCESS":
        logger.info("Scheduled retraining completed successfully")
    else:
        logger.error(f"Scheduled retraining failed with status: {result}")
    
    return result

@flow(name="data-pipeline")
def data_processing_flow():
    """
    Data processing and preparation flow
    """
    logger.info("Starting data processing pipeline")
    
    try:
        # Generate/refresh data
        data_generated = generate_sample_data()
        
        if data_generated:
            logger.info("Data processing completed successfully")
            return "SUCCESS"
        else:
            logger.error("Data processing failed")
            return "FAILED"
            
    except Exception as e:
        logger.error(f"Data processing error: {e}")
        return "ERROR"

if __name__ == "__main__":
    # Run the training flow
    result = training_flow()
    print(f"Training flow result: {result}")
    
    if result != "SUCCESS":
        sys.exit(1)