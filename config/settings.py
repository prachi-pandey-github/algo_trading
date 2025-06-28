"""
Configuration settings for the algorithmic trading system.

This module contains all configurable parameters including:
- Stock tickers (NIFTY 50 stocks)
- Trading parameters
- Technical indicator settings
- Data storage paths
"""

# NIFTY 50 stocks (using NSE symbols for yfinance)
TICKERS = [
    "RELIANCE.NS",    # Reliance Industries
    "TCS.NS",         # Tata Consultancy Services
    "HDFCBANK.NS",    # HDFC Bank
    "INFY.NS",        # Infosys
    "HINDUNILVR.NS",  # Hindustan Unilever
    "ICICIBANK.NS",   # ICICI Bank
    "KOTAKBANK.NS",   # Kotak Mahindra Bank
    "BHARTIARTL.NS",  # Bharti Airtel
    "ITC.NS",         # ITC Limited
    "SBIN.NS",        # State Bank of India
    "LT.NS",          # Larsen & Toubro
    "WIPRO.NS",     # Wipro Limited
    "MARUTI.NS",    # Maruti Suzuki
    "ASIANPAINT.NS", # Asian Paints
    "BAJFINANCE.NS", # Bajaj Finance
    "HCLTECH.NS",   # HCL Technologies
    "POWERGRID.NS", # Power Grid Corporation
    "NTPC.NS",      # NTPC Limited
    "ONGC.NS",      # Oil & Natural Gas Corp
    "TATASTEEL.NS"  # Tata Steel
]
DATA_RANGE = "6mo"  # Data range for fetching historical data (6 months for backtesting)
INTERVAL = "1d"  # Data interval (1d = daily, 1h = hourly, etc.)

# Add CSV storage paths
OUTPUT_DIR = "data/outputs/"
TRADE_LOG_PATH = f"{OUTPUT_DIR}trade_log.csv"
SUMMARY_PATH = f"{OUTPUT_DIR}summary.csv"
ML_RESULTS_PATH = f"{OUTPUT_DIR}ml_results.csv"
INITIAL_CAPITAL = 100000  # Add this line
# Technical indicator settings
RSI_WINDOW = 14
DMA_SHORT = 20
DMA_LONG = 50

# Data directory paths
HISTORICAL_DATA_DIR = "data/historical_data/"
PROCESSED_DATA_DIR = "data/processed/"