"""
Generate sample financial data for InvestWise Predictor
This script creates realistic sample data for training and testing
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_time_series_data(start_date, end_date, freq='ME'):
    """Generate time series index"""
    return pd.date_range(start=start_date, end=end_date, freq=freq)

def generate_gdp_data():
    """Generate GDP data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'QE')
    base_gdp = 12000000  # Base GDP in millions
    
    data = []
    for i, date in enumerate(dates):
        # Add trend and seasonal variation
        trend = base_gdp * (1.02 ** (i/4))  # 2% annual growth
        seasonal = np.sin(2 * np.pi * i / 4) * 100000  # Seasonal variation
        noise = np.random.normal(0, 50000)  # Random noise
        gdp = trend + seasonal + noise
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Quarter': f"Q{date.quarter}",
            'Year': date.year,
            'GDP_Nominal': round(gdp, 2),
            'GDP_Real': round(gdp / (1.03 ** (i/4)), 2),  # Adjust for inflation
            'GDP_Growth_Rate': round(2.0 + np.random.normal(0, 0.5), 2)
        })
    
    return pd.DataFrame(data)

def generate_inflation_data():
    """Generate inflation data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'ME')
    
    data = []
    base_inflation = 5.0
    
    for i, date in enumerate(dates):
        # Add trend and random variation
        trend_inflation = base_inflation + np.sin(2 * np.pi * i / 12) * 1.5
        noise = np.random.normal(0, 0.3)
        inflation_rate = max(0, trend_inflation + noise)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Month': date.strftime('%B'),
            'Year': date.year,
            'Inflation_Rate': round(inflation_rate, 2),
            'Food_Inflation': round(inflation_rate + np.random.normal(2, 0.5), 2),
            'Core_Inflation': round(inflation_rate - np.random.normal(1, 0.3), 2)
        })
    
    return pd.DataFrame(data)

def generate_exchange_rates():
    """Generate exchange rate data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'D')
    
    data = []
    base_usd_kes = 105.0
    base_eur_kes = 120.0
    base_gbp_kes = 135.0
    
    for i, date in enumerate(dates):
        # Add random walk with drift
        usd_change = np.random.normal(0.01, 0.5)
        eur_change = np.random.normal(0.02, 0.6)
        gbp_change = np.random.normal(0.01, 0.7)
        
        base_usd_kes += usd_change
        base_eur_kes += eur_change
        base_gbp_kes += gbp_change
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'USD_KES': round(max(90, base_usd_kes), 4),
            'EUR_KES': round(max(100, base_eur_kes), 4),
            'GBP_KES': round(max(120, base_gbp_kes), 4),
            'JPY_KES': round(max(0.7, base_usd_kes * 0.008), 4)
        })
    
    return pd.DataFrame(data)

def generate_interest_rates():
    """Generate interest rate data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'ME')
    
    data = []
    base_cbr = 9.0
    
    for i, date in enumerate(dates):
        # CBR with policy changes
        cbr_change = np.random.choice([-0.25, 0, 0.25], p=[0.2, 0.6, 0.2])
        base_cbr = max(4.0, min(15.0, base_cbr + cbr_change))
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'CBR': round(base_cbr, 2),
            'Interbank_Rate': round(base_cbr + np.random.normal(0.5, 0.2), 2),
            'TB_91_Days': round(base_cbr + np.random.normal(-0.3, 0.15), 2),
            'TB_182_Days': round(base_cbr + np.random.normal(-0.1, 0.15), 2),
            'TB_364_Days': round(base_cbr + np.random.normal(0.2, 0.15), 2)
        })
    
    return pd.DataFrame(data)

def generate_trade_data():
    """Generate trade data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'ME')
    
    data = []
    for i, date in enumerate(dates):
        exports = np.random.normal(65000, 8000)  # Monthly exports in millions
        imports = np.random.normal(185000, 15000)  # Monthly imports in millions
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Exports_Total': round(max(0, exports), 2),
            'Imports_Total': round(max(0, imports), 2),
            'Trade_Balance': round(exports - imports, 2),
            'Tea_Exports': round(max(0, exports * 0.15 + np.random.normal(0, 1000)), 2),
            'Coffee_Exports': round(max(0, exports * 0.08 + np.random.normal(0, 500)), 2),
            'Horticultural_Exports': round(max(0, exports * 0.25 + np.random.normal(0, 1500)), 2)
        })
    
    return pd.DataFrame(data)

def generate_mobile_payments():
    """Generate mobile payments data"""
    dates = generate_time_series_data('2020-01-01', '2024-12-01', 'ME')
    
    data = []
    base_volume = 450000  # Base monthly volume in millions
    
    for i, date in enumerate(dates):
        # Growth trend for mobile payments
        growth_factor = 1.015 ** i  # 1.5% monthly growth
        volume = base_volume * growth_factor + np.random.normal(0, 20000)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Total_Volume': round(max(0, volume), 2),
            'Person_to_Person': round(max(0, volume * 0.6 + np.random.normal(0, 5000)), 2),
            'Person_to_Business': round(max(0, volume * 0.25 + np.random.normal(0, 3000)), 2),
            'Business_to_Business': round(max(0, volume * 0.15 + np.random.normal(0, 2000)), 2),
            'Active_Agents': int(max(0, 250000 + i * 500 + np.random.normal(0, 2000))),
            'Registered_Customers': int(max(0, 55000000 + i * 50000 + np.random.normal(0, 10000)))
        })
    
    return pd.DataFrame(data)

def create_sample_datasets():
    """Create all sample datasets"""
    datasets = {
        'gdp.csv': generate_gdp_data(),
        'inflation.csv': generate_inflation_data(),
        'exchange_rates.csv': generate_exchange_rates(),
        'interest_rates.csv': generate_interest_rates(),
        'mobile_payments.csv': generate_mobile_payments(),
        'trade_foreign_summary.csv': generate_trade_data()
    }
    
    # Create data directories
    raw_dir = 'data/raw'
    processed_dir = 'data/processed'
    cleaned_dir = 'data/cleaned'
    
    for dir_path in [raw_dir, processed_dir, cleaned_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Save datasets
    for filename, df in datasets.items():
        filepath = os.path.join(raw_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Created {filepath} with {len(df)} rows")
    
    # Create a combined dataset for ML training
    combined_data = create_combined_dataset(datasets)
    combined_filepath = os.path.join(processed_dir, 'combined_features.csv')
    combined_data.to_csv(combined_filepath, index=False)
    print(f"Created {combined_filepath} with {len(combined_data)} rows")
    
    return datasets

def create_combined_dataset(datasets):
    """Combine datasets for ML training"""
    # Start with monthly GDP data (interpolated)
    gdp_monthly = datasets['gdp.csv'].copy()
    gdp_monthly['Date'] = pd.to_datetime(gdp_monthly['Date'])
    gdp_monthly = gdp_monthly.set_index('Date').resample('ME').ffill().reset_index()
    
    # Merge with other monthly data
    inflation = datasets['inflation.csv'].copy()
    inflation['Date'] = pd.to_datetime(inflation['Date'])
    
    mobile = datasets['mobile_payments.csv'].copy()
    mobile['Date'] = pd.to_datetime(mobile['Date'])
    
    rates = datasets['interest_rates.csv'].copy()
    rates['Date'] = pd.to_datetime(rates['Date'])
    
    trade = datasets['trade_foreign_summary.csv'].copy()
    trade['Date'] = pd.to_datetime(trade['Date'])
    
    # Exchange rates - monthly average
    fx = datasets['exchange_rates.csv'].copy()
    fx['Date'] = pd.to_datetime(fx['Date'])
    fx_monthly = fx.set_index('Date').resample('ME').mean().reset_index()
    
    # Merge all datasets
    combined = gdp_monthly[['Date', 'GDP_Nominal', 'GDP_Growth_Rate']].copy()
    combined = combined.merge(inflation[['Date', 'Inflation_Rate', 'Core_Inflation']], on='Date', how='left')
    combined = combined.merge(rates[['Date', 'CBR', 'Interbank_Rate', 'TB_91_Days']], on='Date', how='left')
    combined = combined.merge(fx_monthly[['Date', 'USD_KES', 'EUR_KES']], on='Date', how='left')
    combined = combined.merge(trade[['Date', 'Trade_Balance', 'Exports_Total']], on='Date', how='left')
    combined = combined.merge(mobile[['Date', 'Total_Volume', 'Active_Agents']], on='Date', how='left')
    
    # Create target variable (next month's GDP growth rate)
    combined = combined.sort_values('Date')
    combined['Target_GDP_Growth_Next_Month'] = combined['GDP_Growth_Rate'].shift(-1)
    
    # Drop rows with missing target
    combined = combined.dropna(subset=['Target_GDP_Growth_Next_Month'])
    
    # Add some engineered features
    combined['USD_KES_Change'] = combined['USD_KES'].pct_change()
    combined['Inflation_GDP_Ratio'] = combined['Inflation_Rate'] / combined['GDP_Growth_Rate']
    combined['Trade_GDP_Ratio'] = combined['Trade_Balance'] / combined['GDP_Nominal']
    
    return combined

if __name__ == "__main__":
    print("Generating sample financial data...")
    create_sample_datasets()
    print("Sample data generation complete!")