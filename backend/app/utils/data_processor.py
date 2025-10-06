"""
Data processing utilities
"""
import pandas as pd
import os
from sqlalchemy.orm import Session
from app.crud.market_data import create_market_data
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def load_and_process_data(db: Session, data_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and process data from CSV files into the database
    """
    data_dir = "data/raw"
    processed_types = []
    total_records = 0
    
    # Map of CSV files to data types
    file_mapping = {
        "gdp.csv": "gdp",
        "inflation.csv": "inflation", 
        "exchange_rates.csv": "exchange_rates",
        "interest_rates.csv": "interest_rates",
        "mobile_payments.csv": "mobile_payments",
        "trade_foreign_summary.csv": "trade_foreign_summary"
    }
    
    try:
        for filename, dtype in file_mapping.items():
            # Skip if specific data type requested and this isn't it
            if data_type and dtype != data_type:
                continue
                
            filepath = os.path.join(data_dir, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"Data file not found: {filepath}")
                continue
            
            try:
                # Load CSV data
                df = pd.read_csv(filepath)
                
                if df.empty:
                    logger.warning(f"Empty data file: {filepath}")
                    continue
                
                # Process each row
                records_added = 0
                for _, row in df.iterrows():
                    try:
                        # Convert row to dict and handle date
                        row_data = row.to_dict()
                        
                        # Parse date column
                        date_val = pd.to_datetime(row_data.get('Date', row_data.get('date')))
                        
                        # Create processed data (remove Date from features)
                        processed_data = {k: v for k, v in row_data.items() 
                                        if k.lower() not in ['date', 'index']}
                        
                        # Check if record already exists
                        existing = db.query(
                            "SELECT id FROM market_data WHERE date = %s AND data_type = %s"
                        ).fetchone()
                        
                        if not existing:
                            create_market_data(
                                db=db,
                                date=date_val,
                                data_type=dtype,
                                data_source=filename,
                                raw_data=row_data,
                                processed_data=processed_data
                            )
                            records_added += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing row in {filename}: {e}")
                        continue
                
                processed_types.append(dtype)
                total_records += records_added
                logger.info(f"Processed {records_added} records from {filename}")
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                continue
        
        return {
            "processed_types": processed_types,
            "total_records": total_records
        }
        
    except Exception as e:
        logger.error(f"Error in load_and_process_data: {e}")
        return {"processed_types": [], "total_records": 0}

def prepare_features_for_prediction(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Prepare and validate features for ML prediction
    """
    # Define feature mappings and defaults
    feature_mapping = {
        "gdp_growth_rate": ["GDP_Growth_Rate", "gdp_growth", "growth_rate"],
        "inflation_rate": ["Inflation_Rate", "inflation", "cpi"],
        "usd_kes_rate": ["USD_KES", "usd_kes", "exchange_rate"], 
        "cbr_rate": ["CBR", "cbr", "central_bank_rate"],
        "trade_balance": ["Trade_Balance", "trade_balance", "balance"]
    }
    
    features = {}
    
    for feature_name, possible_keys in feature_mapping.items():
        value = None
        
        # Try to find value using possible keys
        for key in possible_keys:
            if key in data:
                value = data[key]
                break
        
        # Convert to float if found
        if value is not None:
            try:
                features[feature_name] = float(value)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert {feature_name} value {value} to float")
                features[feature_name] = 0.0
        else:
            # Set default value
            default_values = {
                "gdp_growth_rate": 2.0,
                "inflation_rate": 5.0,
                "usd_kes_rate": 110.0,
                "cbr_rate": 9.0,
                "trade_balance": -10000.0
            }
            features[feature_name] = default_values.get(feature_name, 0.0)
    
    return features

def validate_prediction_features(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Validate prediction features and return validation results
    """
    required_features = [
        "gdp_growth_rate", "inflation_rate", "usd_kes_rate", 
        "cbr_rate", "trade_balance"
    ]
    
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required features
    missing_features = [f for f in required_features if f not in features]
    if missing_features:
        validation_result["is_valid"] = False
        validation_result["errors"].append(f"Missing required features: {missing_features}")
    
    # Validate ranges
    feature_ranges = {
        "gdp_growth_rate": (-10.0, 20.0),
        "inflation_rate": (-5.0, 50.0),
        "usd_kes_rate": (50.0, 200.0),
        "cbr_rate": (0.0, 30.0),
        "trade_balance": (-50000.0, 50000.0)
    }
    
    for feature, (min_val, max_val) in feature_ranges.items():
        if feature in features:
            value = features[feature]
            if not (min_val <= value <= max_val):
                validation_result["warnings"].append(
                    f"{feature} value {value} is outside expected range [{min_val}, {max_val}]"
                )
    
    return validation_result