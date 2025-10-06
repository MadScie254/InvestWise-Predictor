"""
Data utilities for ML training
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

def load_financial_data(data_dir: str = "data/raw") -> Dict[str, pd.DataFrame]:
    """
    Load all financial datasets
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary of DataFrames keyed by dataset name
    """
    datasets = {}
    
    file_mapping = {
        "gdp": "gdp.csv",
        "inflation": "inflation.csv",
        "exchange_rates": "exchange_rates.csv", 
        "interest_rates": "interest_rates.csv",
        "mobile_payments": "mobile_payments.csv",
        "trade": "trade_foreign_summary.csv"
    }
    
    for name, filename in file_mapping.items():
        try:
            filepath = f"{data_dir}/{filename}"
            df = pd.read_csv(filepath)
            df['Date'] = pd.to_datetime(df['Date'])
            datasets[name] = df
            logger.info(f"Loaded {name}: {len(df)} records")
        except Exception as e:
            logger.warning(f"Failed to load {filename}: {e}")
    
    return datasets

def merge_datasets(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge all datasets into a single DataFrame for ML training
    
    Args:
        datasets: Dictionary of DataFrames
        
    Returns:
        Merged DataFrame with aligned dates
    """
    # Start with GDP data (quarterly) and resample to monthly
    if "gdp" in datasets:
        base_df = datasets["gdp"].copy()
        base_df = base_df.set_index('Date').resample('M').ffill().reset_index()
        base_df = base_df[['Date', 'GDP_Growth_Rate']].rename(columns={'GDP_Growth_Rate': 'gdp_growth_rate'})
    else:
        # Create dummy base data
        dates = pd.date_range('2020-01-01', '2024-12-01', freq='M')
        base_df = pd.DataFrame({'Date': dates, 'gdp_growth_rate': np.random.normal(2.0, 0.5, len(dates))})
    
    # Merge inflation data
    if "inflation" in datasets:
        inflation_df = datasets["inflation"][['Date', 'Inflation_Rate']].rename(columns={'Inflation_Rate': 'inflation_rate'})
        base_df = base_df.merge(inflation_df, on='Date', how='left')
    
    # Merge exchange rates (take monthly average for daily data)
    if "exchange_rates" in datasets:
        fx_df = datasets["exchange_rates"].copy()
        fx_monthly = fx_df.groupby(fx_df['Date'].dt.to_period('M')).agg({
            'USD_KES': 'mean'
        }).reset_index()
        fx_monthly['Date'] = fx_monthly['Date'].dt.to_timestamp()
        fx_monthly = fx_monthly.rename(columns={'USD_KES': 'usd_kes_rate'})
        base_df = base_df.merge(fx_monthly, on='Date', how='left')
    
    # Merge interest rates
    if "interest_rates" in datasets:
        rates_df = datasets["interest_rates"][['Date', 'CBR']].rename(columns={'CBR': 'cbr_rate'})
        base_df = base_df.merge(rates_df, on='Date', how='left')
    
    # Merge trade data
    if "trade" in datasets:
        trade_df = datasets["trade"][['Date', 'Trade_Balance']].rename(columns={'Trade_Balance': 'trade_balance'})
        base_df = base_df.merge(trade_df, on='Date', how='left')
    
    # Sort by date
    base_df = base_df.sort_values('Date').reset_index(drop=True)
    
    return base_df

def create_target_variable(df: pd.DataFrame, target_col: str = 'gdp_growth_rate', periods: int = 1) -> pd.DataFrame:
    """
    Create target variable for prediction (future values)
    
    Args:
        df: Input DataFrame
        target_col: Column to use for target
        periods: Number of periods to shift forward
        
    Returns:
        DataFrame with target variable
    """
    df_with_target = df.copy()
    df_with_target['target'] = df_with_target[target_col].shift(-periods)
    
    # Remove rows with missing target
    df_with_target = df_with_target.dropna(subset=['target'])
    
    return df_with_target

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features for better model performance
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with additional features
    """
    df_eng = df.copy()
    
    # Lag features
    for col in ['gdp_growth_rate', 'inflation_rate', 'usd_kes_rate']:
        if col in df_eng.columns:
            df_eng[f'{col}_lag1'] = df_eng[col].shift(1)
            df_eng[f'{col}_lag3'] = df_eng[col].shift(3)
    
    # Moving averages
    for col in ['inflation_rate', 'usd_kes_rate', 'cbr_rate']:
        if col in df_eng.columns:
            df_eng[f'{col}_ma3'] = df_eng[col].rolling(window=3).mean()
            df_eng[f'{col}_ma6'] = df_eng[col].rolling(window=6).mean()
    
    # Rate of change
    for col in ['gdp_growth_rate', 'inflation_rate', 'usd_kes_rate']:
        if col in df_eng.columns:
            df_eng[f'{col}_pct_change'] = df_eng[col].pct_change()
    
    # Interaction features
    if 'inflation_rate' in df_eng.columns and 'gdp_growth_rate' in df_eng.columns:
        df_eng['inflation_gdp_ratio'] = df_eng['inflation_rate'] / (df_eng['gdp_growth_rate'] + 1e-6)
    
    if 'cbr_rate' in df_eng.columns and 'inflation_rate' in df_eng.columns:
        df_eng['real_interest_rate'] = df_eng['cbr_rate'] - df_eng['inflation_rate']
    
    # Economic indicators
    if 'trade_balance' in df_eng.columns and 'gdp_growth_rate' in df_eng.columns:
        df_eng['trade_gdp_ratio'] = df_eng['trade_balance'] / (abs(df_eng['gdp_growth_rate']) + 1e-6)
    
    # Volatility measures (rolling standard deviation)
    for col in ['usd_kes_rate', 'inflation_rate']:
        if col in df_eng.columns:
            df_eng[f'{col}_volatility'] = df_eng[col].rolling(window=6).std()
    
    return df_eng

def clean_and_impute_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data and handle missing values
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Remove obvious outliers (values beyond reasonable ranges)
    outlier_bounds = {
        'gdp_growth_rate': (-15, 25),
        'inflation_rate': (-5, 100),
        'usd_kes_rate': (50, 300),
        'cbr_rate': (0, 50),
        'trade_balance': (-200000, 200000)
    }
    
    for col, (lower, upper) in outlier_bounds.items():
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)
    
    # Impute missing values
    numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
    
    # Use median imputation for robustness
    imputer = SimpleImputer(strategy='median')
    df_clean[numeric_columns] = imputer.fit_transform(df_clean[numeric_columns])
    
    return df_clean

def prepare_time_series_data(
    df: pd.DataFrame, 
    sequence_length: int = 12,
    target_col: str = 'target'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare data for LSTM/time series models
    
    Args:
        df: Input DataFrame
        sequence_length: Length of input sequences
        target_col: Target column name
        
    Returns:
        Tuple of (X, y) arrays for time series modeling
    """
    # Select numeric columns (excluding date and target)
    feature_cols = [col for col in df.columns 
                   if col not in ['Date', target_col] and df[col].dtype in ['float64', 'int64']]
    
    X_data = df[feature_cols].values
    y_data = df[target_col].values
    
    X_sequences = []
    y_sequences = []
    
    for i in range(sequence_length, len(X_data)):
        X_sequences.append(X_data[i-sequence_length:i])
        y_sequences.append(y_data[i])
    
    return np.array(X_sequences), np.array(y_sequences)

def create_train_test_split(
    df: pd.DataFrame, 
    test_size: float = 0.2,
    time_series: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create train/test split preserving time order for time series data
    
    Args:
        df: Input DataFrame
        test_size: Fraction of data for testing
        time_series: Whether to preserve time order
        
    Returns:
        Tuple of (train_df, test_df)
    """
    if time_series:
        # Split based on time to avoid data leakage
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()
    else:
        # Random split
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    
    return train_df, test_df

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality and return quality metrics
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with data quality metrics
    """
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'date_range': {
            'start': df['Date'].min() if 'Date' in df.columns else None,
            'end': df['Date'].max() if 'Date' in df.columns else None
        }
    }
    
    # Check for data gaps (if Date column exists)
    if 'Date' in df.columns:
        df_sorted = df.sort_values('Date')
        date_diff = df_sorted['Date'].diff()
        expected_freq = date_diff.mode().iloc[0] if len(date_diff.mode()) > 0 else pd.Timedelta(days=30)
        large_gaps = (date_diff > expected_freq * 2).sum()
        quality_report['data_gaps'] = large_gaps
    
    return quality_report