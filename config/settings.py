"""
Configuration settings for the algorithmic trading system.

This module contains all configurable parameters including:
- Stock tickers (NIFTY 50 stocks)
- Trading parameters
- Technical indicator settings
- Data storage paths
"""

TICKERS = [
    "RELIANCE.NS",    # Reliance Industries
    "HDFCBANK.NS",    # HDFC Bank
    "TCS.NS",         # Tata Consultancy Services
    "INFY.NS",        # Infosys
    "HINDUNILVR.NS",  # Hindustan Unilever
    "ICICIBANK.NS",   # ICICI Bank
    "BHARTIARTL.NS",  # Bharti Airtel
    "ITC.NS",         # ITC Limited
    "BAJFINANCE.NS",  # Bajaj Finance
    "WIPRO.NS",       # Wipro Limited
    "HCLTECH.NS",     # HCL Technologies
    "SBIN.NS",        # State Bank of India
    "LT.NS",          # Larsen & Toubro
    "AXISBANK.NS",    # Axis Bank
    "ASIANPAINT.NS"   # Asian Paints
]
DATA_RANGE = "6mo"  # Data range for 6 months backtesting as per requirement
INTERVAL = "1d"  # Daily data for Indian market

# Indian Market Settings
MARKET_OPEN = "09:15"  # Indian market opening time
MARKET_CLOSE = "15:30"  # Indian market closing time
TIMEZONE = "Asia/Kolkata"  # Indian timezone

# Add CSV storage paths
OUTPUT_DIR = "data/outputs/"
TRADE_LOG_PATH = f"{OUTPUT_DIR}trade_log.csv"
SUMMARY_PATH = f"{OUTPUT_DIR}summary.csv"
ML_RESULTS_PATH = f"{OUTPUT_DIR}ml_results.csv"
INITIAL_CAPITAL = 100000  
# Technical indicator settings
RSI_WINDOW = 14
DMA_SHORT = 20
DMA_LONG = 50

# Data directory paths
HISTORICAL_DATA_DIR = "data/historical_data/"
PROCESSED_DATA_DIR = "data/processed/"
