import pandas as pd
import numpy as np

def validate_sensor_data(df: pd.DataFrame) -> dict:
    """
    Performs automatic schema and quality validation checks on incoming sensor logs.
    """
    missing_count = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()
    
    # Generate a simple quality score metrics overview
    quality_score = 100 - (min((missing_count + duplicate_count) / len(df) * 100, 100))
    
    return {
        "missing_values": int(missing_count),
        "duplicates": int(duplicate_count),
        "data_quality_score": float(quality_score)
    }

def engineer_industrial_features(df: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
    """
    Transforms raw sensor timelines into predictive temporal features.
    Assumes df has columns: 'temperature', 'pressure', 'vibration'
    """
    processed_df = df.copy()
    
    # 1. Rolling window statistics
    processed_df['temp_rolling_mean'] = processed_df['temperature'].rolling(window=window_size).mean()
    processed_df['vibration_rolling_std'] = processed_df['vibration'].rolling(window=window_size).std()
    
    # 2. Lag features (capturing sudden operational shifts)
    processed_df['pressure_lag_1'] = processed_df['pressure'].shift(1)
    
    # 3. Domain ratios
    processed_df['temp_pressure_ratio'] = processed_df['temperature'] / (processed_df['pressure'] + 1e-5)
    
    # Drop rows with NaN values introduced by rolling windows
    processed_df.dropna(inplace=True)
    
    return processed_df

if __name__ == "__main__":
    print("Industrial feature engineering pipeline initialized successfully.")