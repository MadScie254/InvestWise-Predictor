"""
ML Training Pipeline for InvestWise Predictor
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import lightgbm as lgb
import xgboost as xgb
import joblib
import mlflow
import mlflow.sklearn
import mlflow.lightgbm
import mlflow.xgboost
from datetime import datetime
import logging
from typing import Dict, Any, Tuple
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestWiseTrainer:
    """Training pipeline for investment prediction models"""
    
    def __init__(self, data_path: str = None, mlflow_uri: str = None):
        self.data_path = data_path or "data/processed/combined_features.csv"
        self.mlflow_uri = mlflow_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.models_dir = "ml/training/artifacts"
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(self.mlflow_uri)
        
        # Create artifacts directory
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.feature_names = [
            "gdp_growth_rate", "inflation_rate", "usd_kes_rate", 
            "cbr_rate", "trade_balance"
        ]
        self.target_name = "Target_GDP_Growth_Next_Month"
    
    def load_and_prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and prepare training data"""
        logger.info(f"Loading data from {self.data_path}")
        
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df)} records")
        
        # Check for required columns
        missing_cols = [col for col in self.feature_names + [self.target_name] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Remove rows with missing values
        df_clean = df[self.feature_names + [self.target_name]].dropna()
        logger.info(f"After cleaning: {len(df_clean)} records")
        
        # Prepare features and target
        X = df_clean[self.feature_names]
        y = df_clean[self.target_name]
        
        return X, y
    
    def create_feature_engineered_data(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create additional engineered features"""
        X_eng = X.copy()
        
        # Interaction features
        X_eng['inflation_gdp_ratio'] = X_eng['inflation_rate'] / (X_eng['gdp_growth_rate'] + 1e-6)
        X_eng['usd_inflation_interaction'] = X_eng['usd_kes_rate'] * X_eng['inflation_rate']
        X_eng['cbr_inflation_diff'] = X_eng['cbr_rate'] - X_eng['inflation_rate']
        
        # Polynomial features for key indicators
        X_eng['gdp_growth_squared'] = X_eng['gdp_growth_rate'] ** 2
        X_eng['inflation_squared'] = X_eng['inflation_rate'] ** 2
        
        # Economic stress indicators
        X_eng['economic_stress'] = (
            (X_eng['inflation_rate'] > 7) & 
            (X_eng['gdp_growth_rate'] < 2)
        ).astype(int)
        
        return X_eng
    
    def train_linear_model(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train Linear Regression model"""
        logger.info("Training Linear Regression model")
        
        with mlflow.start_run(run_name="linear_regression"):
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            metrics = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test)
            }
            
            # Log parameters and metrics
            mlflow.log_param("model_type", "LinearRegression")
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Save model
            model_path = os.path.join(self.models_dir, "linear_model.joblib")
            joblib.dump(model, model_path)
            mlflow.log_artifact(model_path)
            mlflow.sklearn.log_model(model, "model")
            
            return {"model": model, "metrics": metrics}
    
    def train_random_forest(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train Random Forest model with hyperparameter tuning"""
        logger.info("Training Random Forest model")
        
        with mlflow.start_run(run_name="random_forest"):
            # Hyperparameter tuning
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            rf = RandomForestRegressor(random_state=42)
            grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            
            model = grid_search.best_estimator_
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            metrics = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test)
            }
            
            # Log parameters and metrics
            mlflow.log_param("model_type", "RandomForest")
            mlflow.log_params(grid_search.best_params_)
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Feature importance
            feature_importance = dict(zip(X_train.columns, model.feature_importances_))
            mlflow.log_dict(feature_importance, "feature_importance.json")
            
            # Save model
            model_path = os.path.join(self.models_dir, "random_forest_model.joblib")
            joblib.dump(model, model_path)
            mlflow.log_artifact(model_path)
            mlflow.sklearn.log_model(model, "model")
            
            return {"model": model, "metrics": metrics, "feature_importance": feature_importance}
    
    def train_lightgbm(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train LightGBM model"""
        logger.info("Training LightGBM model")
        
        with mlflow.start_run(run_name="lightgbm"):
            # LightGBM parameters
            params = {
                'objective': 'regression',
                'metric': 'rmse',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1,
                'random_state': 42
            }
            
            # Create datasets
            train_data = lgb.Dataset(X_train, label=y_train)
            valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
            
            # Train model
            model = lgb.train(
                params,
                train_data,
                valid_sets=[train_data, valid_data],
                valid_names=['train', 'eval'],
                num_boost_round=1000,
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)]
            )
            
            # Predictions
            y_pred_train = model.predict(X_train, num_iteration=model.best_iteration)
            y_pred_test = model.predict(X_test, num_iteration=model.best_iteration)
            
            # Metrics
            metrics = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test),
                'best_iteration': model.best_iteration
            }
            
            # Log parameters and metrics
            mlflow.log_params(params)
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Feature importance
            feature_importance = dict(zip(X_train.columns, model.feature_importance()))
            mlflow.log_dict(feature_importance, "feature_importance.json")
            
            # Save model
            model_path = os.path.join(self.models_dir, "lightgbm_model.joblib")
            joblib.dump(model, model_path)
            mlflow.log_artifact(model_path)
            mlflow.lightgbm.log_model(model, "model")
            
            return {"model": model, "metrics": metrics, "feature_importance": feature_importance}
    
    def train_xgboost(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train XGBoost model"""
        logger.info("Training XGBoost model")
        
        with mlflow.start_run(run_name="xgboost"):
            # XGBoost parameters
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'n_estimators': 1000
            }
            
            model = xgb.XGBRegressor(**params)
            
            # Train with early stopping
            model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_test, y_test)],
                eval_metric='rmse',
                early_stopping_rounds=50,
                verbose=False
            )
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            metrics = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test),
                'best_iteration': model.best_iteration
            }
            
            # Log parameters and metrics
            mlflow.log_params(params)
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Feature importance
            feature_importance = dict(zip(X_train.columns, model.feature_importances_))
            mlflow.log_dict(feature_importance, "feature_importance.json")
            
            # Save model
            model_path = os.path.join(self.models_dir, "xgboost_model.joblib")
            joblib.dump(model, model_path)
            mlflow.log_artifact(model_path)
            mlflow.xgboost.log_model(model, "model")
            
            return {"model": model, "metrics": metrics, "feature_importance": feature_importance}
    
    def register_best_model(self, model_results: Dict[str, Dict]) -> str:
        """Register the best performing model"""
        # Find best model based on test RMSE
        best_model_name = min(model_results.keys(), 
                             key=lambda x: model_results[x]["metrics"]["test_rmse"])
        
        best_metrics = model_results[best_model_name]["metrics"]
        logger.info(f"Best model: {best_model_name} (test RMSE: {best_metrics['test_rmse']:.4f})")
        
        # Register model in MLflow
        model_name = "investwise_model"
        
        # Get the run ID for the best model
        runs = mlflow.search_runs(filter_string=f"tags.mlflow.runName = '{best_model_name}'")
        if not runs.empty:
            run_id = runs.iloc[0]['run_id']
            model_uri = f"runs:/{run_id}/model"
            
            try:
                mlflow.register_model(model_uri, model_name)
                logger.info(f"Registered {best_model_name} as {model_name}")
            except Exception as e:
                logger.error(f"Failed to register model: {e}")
        
        return best_model_name
    
    def train_all_models(self) -> Dict[str, Dict]:
        """Train all models and return results"""
        logger.info("Starting training pipeline")
        
        # Set MLflow experiment
        experiment_name = "investwise_training"
        mlflow.set_experiment(experiment_name)
        
        # Load and prepare data
        X, y = self.load_and_prepare_data()
        
        # Feature engineering
        X_engineered = self.create_feature_engineered_data(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_engineered, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
        
        # Save scaler
        scaler_path = os.path.join(self.models_dir, "scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        
        logger.info(f"Training data shape: {X_train.shape}")
        logger.info(f"Test data shape: {X_test.shape}")
        
        # Train models
        model_results = {}
        
        try:
            model_results["linear_regression"] = self.train_linear_model(
                X_train_scaled, X_test_scaled, y_train, y_test
            )
        except Exception as e:
            logger.error(f"Linear regression training failed: {e}")
        
        try:
            model_results["random_forest"] = self.train_random_forest(
                X_train, X_test, y_train, y_test
            )
        except Exception as e:
            logger.error(f"Random forest training failed: {e}")
        
        try:
            model_results["lightgbm"] = self.train_lightgbm(
                X_train, X_test, y_train, y_test
            )
        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")
        
        try:
            model_results["xgboost"] = self.train_xgboost(
                X_train, X_test, y_train, y_test
            )
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}")
        
        # Register best model
        if model_results:
            self.register_best_model(model_results)
        
        # Print results summary
        logger.info("\n" + "="*50)
        logger.info("TRAINING RESULTS SUMMARY")
        logger.info("="*50)
        
        for model_name, result in model_results.items():
            metrics = result["metrics"]
            logger.info(f"\n{model_name.upper()}:")
            logger.info(f"  Test RMSE: {metrics['test_rmse']:.4f}")
            logger.info(f"  Test MAE:  {metrics['test_mae']:.4f}")
            logger.info(f"  Test R²:   {metrics['test_r2']:.4f}")
        
        return model_results

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train InvestWise prediction models")
    parser.add_argument("--data-path", type=str, help="Path to training data CSV")
    parser.add_argument("--mlflow-uri", type=str, help="MLflow tracking URI")
    
    args = parser.parse_args()
    
    trainer = InvestWiseTrainer(
        data_path=args.data_path,
        mlflow_uri=args.mlflow_uri
    )
    
    results = trainer.train_all_models()
    
    if results:
        logger.info("Training completed successfully!")
    else:
        logger.error("Training failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())