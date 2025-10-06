"""
Model loading and management
"""
import os
import joblib
import mlflow
import mlflow.sklearn
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages ML models loading and serving"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.current_model = None
        self.mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(self.mlflow_uri)
        
    def load_default_model(self) -> bool:
        """Load the default model"""
        try:
            # Try loading from MLflow first
            if self._load_from_mlflow("latest"):
                return True
            
            # Fallback to local model
            return self._load_local_model()
            
        except Exception as e:
            logger.error(f"Failed to load default model: {e}")
            return False
    
    def _load_from_mlflow(self, version: str = "latest") -> bool:
        """Load model from MLflow"""
        try:
            model_name = os.getenv("MODEL_NAME", "investwise_model")
            
            if version == "latest":
                model_uri = f"models:/{model_name}/latest"
            else:
                model_uri = f"models:/{model_name}/{version}"
            
            logger.info(f"Loading model from MLflow: {model_uri}")
            model = mlflow.sklearn.load_model(model_uri)
            
            self.models[version] = model
            self.current_model = model
            
            logger.info(f"Successfully loaded model {model_name}:{version} from MLflow")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load model from MLflow: {e}")
            return False
    
    def _load_local_model(self) -> bool:
        """Load model from local file system"""
        try:
            model_paths = [
                "models/model.joblib",
                "models/investwise_model.joblib",
                "../models/model.joblib"
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path):
                    logger.info(f"Loading model from local file: {model_path}")
                    model = joblib.load(model_path)
                    
                    self.models["local"] = model
                    self.current_model = model
                    
                    logger.info(f"Successfully loaded local model from {model_path}")
                    return True
            
            # If no model file found, create a dummy model for testing
            logger.warning("No model file found, creating dummy model")
            return self._create_dummy_model()
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            return False
    
    def _create_dummy_model(self) -> bool:
        """Create a dummy model for testing purposes"""
        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np
            
            # Create simple linear regression model
            X_dummy = np.random.randn(100, 5)
            y_dummy = X_dummy.sum(axis=1) + np.random.randn(100) * 0.1
            
            model = LinearRegression()
            model.fit(X_dummy, y_dummy)
            
            self.models["dummy"] = model
            self.current_model = model
            
            logger.info("Created dummy model for testing")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dummy model: {e}")
            return False
    
    def load_model(self, version: str) -> bool:
        """Load a specific model version"""
        try:
            # Try MLflow first
            if self._load_from_mlflow(version):
                return True
            
            # Try local file
            model_path = f"models/{version}.joblib"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                self.models[version] = model
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to load model {version}: {e}")
            return False
    
    def get_model(self, version: str = "latest"):
        """Get a loaded model"""
        if version == "latest":
            return self.current_model
        
        if version in self.models:
            return self.models[version]
        
        # Try to load the model if not found
        if self.load_model(version):
            return self.models[version]
        
        return None
    
    def is_model_loaded(self) -> bool:
        """Check if any model is loaded"""
        return self.current_model is not None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        models_info = []
        
        # Add loaded models
        for version, model in self.models.items():
            models_info.append({
                "name": "investwise_model",
                "version": version,
                "status": "loaded",
                "last_updated": datetime.now().isoformat(),
                "metrics": self._get_model_metrics(model)
            })
        
        # Try to get models from MLflow
        try:
            client = mlflow.tracking.MlflowClient()
            model_name = os.getenv("MODEL_NAME", "investwise_model")
            
            try:
                versions = client.get_latest_versions(model_name)
                for version in versions:
                    if version.version not in [m["version"] for m in models_info]:
                        models_info.append({
                            "name": model_name,
                            "version": version.version,
                            "status": "available",
                            "last_updated": version.last_updated_timestamp,
                            "metrics": None
                        })
            except Exception as e:
                logger.debug(f"No MLflow models found: {e}")
                
        except Exception as e:
            logger.warning(f"Failed to query MLflow: {e}")
        
        return models_info
    
    def _get_model_metrics(self, model) -> Optional[Dict[str, float]]:
        """Get basic metrics for a model"""
        try:
            # This is a placeholder - in practice, you'd store metrics during training
            if hasattr(model, 'score'):
                return {"type": type(model).__name__}
            return None
        except Exception:
            return None