"""
Data loading and technical indicator calculation module.

This module handles:
- Stock data fetching from Yahoo Finance
- Technical indicator calculations (RSI, MACD, Moving Averages, etc.)
- Data preprocessing and validation
"""

import pandas as pd
import yfinance as yf
import numpy as np
import os
from config import settings
from datetime import datetime, timedelta

def fetch_stock_data(ticker, period=settings.DATA_RANGE, interval=settings.INTERVAL, source="yfinance"):
    """
    Fetch historical stock data from specified source
    Args:
        ticker (str): Stock ticker symbol
        period (str): Time period to fetch (default: "6mo")
        interval (str): Data interval (1d, 1h, etc.) (default: "1d")
        source (str): Data source ("yfinance", "alpha_vantage", or "csv")
    Returns:
        pd.DataFrame: Historical stock data with datetime index
    """
    try:
        print(f"[DEBUG] Fetching data for {ticker} | period={period} | interval={interval} | source={source}")
        if source.lower() == "yfinance":
            df = _fetch_from_yfinance(ticker, period, interval)
            print(f"[DEBUG] Data shape for {ticker}: {df.shape}")
            if df.empty:
                print(f"[INFO] No data for {ticker}, trying fallback ticker 'RELIANCE.NS' for connectivity test.")
                fallback_df = _fetch_from_yfinance('RELIANCE.NS', period, interval)
                print(f"[DEBUG] Fallback AAPL data shape: {fallback_df.shape}")
                if not fallback_df.empty:
                    print("[SUGGESTION] Issue might be with NSE market hours or connectivity. Check if market is open and try again.")
                else:
                    print("[ERROR] yfinance is not returning data for any ticker. Check your internet connection or yfinance version.")
            return df
        elif source.lower() == "csv":
            file_path = os.path.join(settings.HISTORICAL_DATA_DIR, f"{ticker}.csv")
            print(f"[DEBUG] Loading from CSV: {file_path}")
            return load_from_csv(file_path)
        else:
            raise ValueError(f"Invalid data source: {source}")
    except Exception as e:
        print(f"[ERROR] Exception fetching data for {ticker}: {e}")
        return pd.DataFrame()

def _fetch_from_yfinance(ticker, period, interval):
    """Fetch data using Yahoo Finance API"""
    print(f"[DEBUG] Using yfinance to fetch {ticker} | period={period} | interval={interval}")
    stock = yf.Ticker(ticker)
    try:
        df = stock.history(period=period, interval=interval)
        print(f"[DEBUG] yfinance returned shape: {df.shape} for {ticker}")
        if df.empty:
            print(f"[WARNING] No data found for {ticker} with yfinance. Trying fallback period/interval...")
            # Try fallback period and interval
            fallback_period = "1mo"
            fallback_interval = "1d"
            df = stock.history(period=fallback_period, interval=fallback_interval)
            print(f"[DEBUG] Fallback yfinance returned shape: {df.shape} for {ticker} (period={fallback_period}, interval={fallback_interval})")
            if df.empty:
                print(f"[ERROR] Still no data for {ticker} with fallback period/interval.")
                raise ValueError(f"No data found for {ticker} (even with fallback period/interval)")
        # Clean and format data
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.index.name = "Date"
        return df
    except Exception as e:
        print(f"[ERROR] Exception in _fetch_from_yfinance for {ticker}: {e}")
        raise

def calculate_technical_indicators(df):
    """
    Calculate technical indicators (RSI, DMAs, MACD)
    Args:
        df (pd.DataFrame): Stock data with OHLC columns
    Returns:
        pd.DataFrame: DataFrame with added technical indicators
    """
    if df.empty:
        return df
    
    # Calculate price changes
    delta = df['Close'].diff()
    
    # Calculate RSI using Wilder's smoothing (EMA)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate EMA for gains and losses
    avg_gain = gain.ewm(alpha=1/settings.RSI_WINDOW, min_periods=settings.RSI_WINDOW, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/settings.RSI_WINDOW, min_periods=settings.RSI_WINDOW, adjust=False).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate moving averages
    df['DMA_20'] = df['Close'].rolling(window=settings.DMA_SHORT).mean()
    df['DMA_50'] = df['Close'].rolling(window=settings.DMA_LONG).mean()
    
    # Calculate MACD (Moving Average Convergence Divergence)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # Calculate Volume Moving Average for volume analysis
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    
    # Calculate Bollinger Bands
    bb_period = 20
    bb_std = 2
    df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
    bb_std_dev = df['Close'].rolling(window=bb_period).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std_dev * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std_dev * bb_std)
    
    # Handle NaN values more intelligently for short datasets
    # We need at least RSI_WINDOW (14) rows for RSI calculation
    if len(df) < settings.RSI_WINDOW:
        print(f"Warning: Not enough data for RSI calculation. Need {settings.RSI_WINDOW}, got {len(df)}")
        return pd.DataFrame()
    
    # Only keep rows where we have essential indicators (RSI and short MA)
    # For longer MA (50-day), we'll use what we have or skip that condition
    essential_cols = ['RSI', 'DMA_20']
    df_clean = df.dropna(subset=essential_cols)
    
    # Fill remaining NaN values using forward fill method
    df_clean = df_clean.ffill()
    
    return df_clean

def load_from_csv(file_path):
    """
    Load stock data from a CSV file
    Args:
        file_path (str): Path to CSV file
    Returns:
        pd.DataFrame: Stock data with datetime index
    """
    try:
        df = pd.read_csv(file_path)
        
        # Check if index column exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
        elif 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df.set_index('Datetime')
        else:
            df.index = pd.to_datetime(df.index)
            
        # Ensure required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def save_to_csv(df, file_path):
    """
    Save DataFrame to CSV
    Args:
        df (pd.DataFrame): Data to save
        file_path (str): Output file path
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Reset index for CSV format
        df.reset_index(inplace=True)
        if 'index' in df.columns:
            df.drop(columns=['index'], inplace=True)
            
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def update_historical_data(ticker, period="6mo", interval="1d", source="yfinance"):
    """
    Update or create historical data file
    Args:
        ticker (str): Stock ticker
        period (str): Time period
        interval (str): Data interval
        source (str): Data source
    Returns:
        str: Path to saved file
    """
    # Create directory if needed
    os.makedirs(settings.HISTORICAL_DATA_DIR, exist_ok=True)
    file_path = os.path.join(settings.HISTORICAL_DATA_DIR, f"{ticker}.csv")
    
    # Fetch new data
    new_data = fetch_stock_data(ticker, period, interval, source)
    
    if new_data.empty:
        print(f"No data fetched for {ticker}")
        return ""
    
    # Save to CSV
    save_to_csv(new_data, file_path)
    return file_path

def get_processed_data(ticker, recalculate=False):
    """
    Get processed data with technical indicators
    Args:
        ticker (str): Stock ticker
        recalculate (bool): Force new calculation
    Returns:
        pd.DataFrame: Processed data with indicators
    """
    # Check if processed data exists
    processed_path = os.path.join(settings.PROCESSED_DATA_DIR, f"{ticker}_processed.csv")
    
    if not recalculate and os.path.exists(processed_path):
        try:
            return load_from_csv(processed_path)
        except:
            print("Error loading processed data, recalculating...")
    
    # Fetch and process data
    raw_data = fetch_stock_data(ticker)
    processed_data = calculate_technical_indicators(raw_data)
    
    # Save processed data
    save_to_csv(processed_data, processed_path)
    return processed_data

def get_intraday_data(ticker, days=5, interval="1h"):
    """
    Get recent intraday data
    Args:
        ticker (str): Stock ticker
        days (int): Number of days to fetch
        interval (str): Data interval (1h, 30m, 15m, 5m)
    Returns:
        pd.DataFrame: Intraday data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    period = f"{days}d"
    
    # Fetch data
    df = fetch_stock_data(ticker, period=period, interval=interval)
    
    if df.empty:
        return df
    
    # Filter to market hours (if needed)
    if interval != "1d":
        df = df.between_time('09:30', '16:00')
    
    return df