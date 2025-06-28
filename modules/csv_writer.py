"""
CSV data logging and persistence module.

This module handles:
- Trade logging to CSV files
- Performance summary tracking
- ML model results logging
- Data export functionality
"""

import pandas as pd
import os
from config import settings

def initialize_csv_files():
    """Create output directory and initialize CSV files with headers"""
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Initialize Trade Log CSV
    if not os.path.exists(settings.TRADE_LOG_PATH):
        pd.DataFrame(columns=[
            'Timestamp', 'Ticker', 'Signal', 'Price', 
            'Quantity', 'PnL', 'RSI', 'DMA_20', 'DMA_50', 'MACD', 'Volume_Ratio'
        ]).to_csv(settings.TRADE_LOG_PATH, index=False)
    
    # Initialize Summary CSV
    if not os.path.exists(settings.SUMMARY_PATH):
        pd.DataFrame(columns=[
            'Ticker', 'StartDate', 'EndDate', 'InitialCapital',
            'FinalValue', 'ReturnPct', 'WinRate', 'TotalTrades'
        ]).to_csv(settings.SUMMARY_PATH, index=False)
    
    # Initialize ML Results CSV
    if not os.path.exists(settings.ML_RESULTS_PATH):
        pd.DataFrame(columns=[
            'Timestamp', 'Ticker', 'Accuracy', 'Features'
        ]).to_csv(settings.ML_RESULTS_PATH, index=False)

def log_trade(trade_data):
    """Append trade to CSV log"""
    try:
        # Use append mode for better performance
        df = pd.DataFrame([trade_data])
        df.to_csv(settings.TRADE_LOG_PATH, mode='a', header=False, index=False)
    except Exception as e:
        print(f"Error logging trade: {e}")

def log_summary(summary_data):
    """Append strategy summary"""
    try:
        df = pd.DataFrame([summary_data])
        df.to_csv(settings.SUMMARY_PATH, mode='a', header=False, index=False)
    except Exception as e:
        print(f"Error logging summary: {e}")

def log_ml_results(ml_data):
    """Append ML results"""
    try:
        df = pd.DataFrame([ml_data])
        df.to_csv(settings.ML_RESULTS_PATH, mode='a', header=False, index=False)
    except Exception as e:
        print(f"Error logging ML results: {e}")