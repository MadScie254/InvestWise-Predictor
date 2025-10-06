"""
Model explainability using SHAP
"""
import shap
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ExplainerManager:
    """Manages model explainers for interpretability"""
    
    def __init__(self):
        self.explainers: Dict[str, Any] = {}
    
    def explain_prediction(
        self, 
        model, 
        features: List[float], 
        feature_names: List[str],
        max_display: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Generate SHAP explanations for a prediction
        
        Args:
            model: The ML model
            features: Input feature values
            feature_names: Names of the features
            max_display: Maximum number of features to include in explanation
            
        Returns:
            Dictionary with SHAP values and interpretation
        """
        try:
            # Convert features to numpy array
            X = np.array([features])
            
            # Get or create explainer for this model
            model_id = id(model)
            
            if model_id not in self.explainers:
                self.explainers[model_id] = self._create_explainer(model, X)
            
            explainer = self.explainers[model_id]
            
            if explainer is None:
                return None
            
            # Generate SHAP values
            shap_values = explainer.shap_values(X)
            
            # Handle different types of SHAP values
            if isinstance(shap_values, list):
                # For classification models, take the first class
                shap_values = shap_values[0] if len(shap_values) > 0 else shap_values
            
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]  # Take first sample
            
            # Create feature importance ranking
            abs_shap_values = np.abs(shap_values)
            feature_importance = list(zip(feature_names, shap_values, abs_shap_values))
            feature_importance.sort(key=lambda x: x[2], reverse=True)
            
            # Limit to max_display features
            feature_importance = feature_importance[:max_display]
            
            explanation = {
                "shap_values": [
                    {
                        "feature": name,
                        "value": float(features[feature_names.index(name)]),
                        "shap_value": float(shap_val),
                        "importance": float(abs_shap_val)
                    }
                    for name, shap_val, abs_shap_val in feature_importance
                ],
                "base_value": float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0.0,
                "prediction_explanation": self._generate_text_explanation(feature_importance),
                "total_impact": float(np.sum(shap_values))
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return None
    
    def _create_explainer(self, model, sample_data: np.ndarray):
        """Create appropriate SHAP explainer for the model"""
        try:
            # Try tree explainer first (for tree-based models)
            if hasattr(model, 'tree_') or 'tree' in str(type(model)).lower():
                return shap.TreeExplainer(model)
            
            # Try linear explainer for linear models
            if hasattr(model, 'coef_') or 'linear' in str(type(model)).lower():
                return shap.LinearExplainer(model, sample_data)
            
            # Fallback to kernel explainer (model-agnostic but slower)
            logger.info("Using KernelExplainer (may be slow)")
            return shap.KernelExplainer(model.predict, sample_data[:1])
            
        except Exception as e:
            logger.warning(f"Failed to create SHAP explainer: {e}")
            return None
    
    def _generate_text_explanation(self, feature_importance: List[tuple]) -> str:
        """Generate human-readable explanation from SHAP values"""
        try:
            if not feature_importance:
                return "No explanation available."
            
            explanations = []
            
            for i, (feature_name, shap_value, abs_shap_value) in enumerate(feature_importance[:3]):
                impact = "increases" if shap_value > 0 else "decreases"
                strength = "strongly" if abs_shap_value > 0.1 else "moderately" if abs_shap_value > 0.05 else "slightly"
                
                # Make feature names more readable
                readable_name = feature_name.replace('_', ' ').title()
                
                explanations.append(f"{readable_name} {strength} {impact} the prediction")
            
            if len(explanations) == 1:
                return explanations[0] + "."
            elif len(explanations) == 2:
                return " and ".join(explanations) + "."
            else:
                return ", ".join(explanations[:-1]) + f", and {explanations[-1]}."
                
        except Exception as e:
            logger.error(f"Error generating text explanation: {e}")
            return "Unable to generate explanation."
    
    def clear_explainers(self):
        """Clear cached explainers"""
        self.explainers.clear()
    
    def get_global_feature_importance(
        self, 
        model, 
        sample_data: np.ndarray, 
        feature_names: List[str],
        n_samples: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Generate global feature importance using SHAP
        
        Args:
            model: The ML model
            sample_data: Sample data for background
            feature_names: Names of features
            n_samples: Number of samples to use for analysis
            
        Returns:
            Global feature importance analysis
        """
        try:
            model_id = id(model)
            
            if model_id not in self.explainers:
                self.explainers[model_id] = self._create_explainer(model, sample_data[:10])
            
            explainer = self.explainers[model_id]
            
            if explainer is None:
                return None
            
            # Use subset of sample data
            analysis_data = sample_data[:min(n_samples, len(sample_data))]
            
            # Generate SHAP values for the dataset
            shap_values = explainer.shap_values(analysis_data)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Calculate mean absolute SHAP values for each feature
            mean_shap_values = np.mean(np.abs(shap_values), axis=0)
            
            # Create feature importance ranking
            importance_data = list(zip(feature_names, mean_shap_values))
            importance_data.sort(key=lambda x: x[1], reverse=True)
            
            return {
                "feature_importance": [
                    {
                        "feature": name,
                        "importance": float(importance)
                    }
                    for name, importance in importance_data
                ],
                "total_samples_analyzed": len(analysis_data),
                "most_important_feature": importance_data[0][0] if importance_data else None
            }
            
        except Exception as e:
            logger.error(f"Error generating global feature importance: {e}")
            return None