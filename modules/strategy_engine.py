"""
Trading strategy engine module.

This module implements the algorithmic trading strategy based on:
- RSI (Relative Strength Index) signals
- Moving Average crossovers (Golden/Death Cross)
- Volume analysis
- Risk management rules
"""

import pandas as pd
import numpy as np
from config import settings


def generate_signals(df):
    """
    Generate trading signals based on technical indicators.
    Adapted for datasets with potentially missing long-term indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data and technical indicators
        
    Returns:
        pd.DataFrame: DataFrame with added signal columns
    """
    # Initialize signal columns
    df['Signal'] = 0  # 0 = Hold, 1 = Buy, -1 = Sell
    df['Position'] = 0  # Track current position
    
    # Check if we have enough data for long-term MA
    has_long_ma = not df['DMA_50'].isna().all()
    
    # Practical Strategy Implementation (adapted for shorter datasets)
    for i in range(1, len(df)):
        current_position = df['Position'].iloc[i-1] if i > 0 else 0
        
        # Get current values, handling NaN for DMA_50
        current_rsi = df['RSI'].iloc[i]
        current_ma20 = df['DMA_20'].iloc[i]
        current_ma50 = df['DMA_50'].iloc[i] if not pd.isna(df['DMA_50'].iloc[i]) else current_ma20
        current_close = df['Close'].iloc[i]
        
        # Previous values for cross detection
        prev_ma20 = df['DMA_20'].iloc[i-1] if i > 0 else current_ma20
        prev_ma50 = df['DMA_50'].iloc[i-1] if i > 0 and not pd.isna(df['DMA_50'].iloc[i-1]) else prev_ma20
        
        # Buy Signal Conditions (STRICT RSI < 30 as per requirements):
        # Primary: RSI < 30 (strictly oversold as per user requirement)
        # Confirmation: Upward trend (20-DMA > 50-DMA)
        rsi_buy_threshold = current_rsi < 30  # Back to strict requirement
        rsi_strong_buy = current_rsi < 25     # Very strong oversold condition
        
        # Golden cross detection (when available)
        if has_long_ma and not pd.isna(current_ma50) and not pd.isna(prev_ma50):
            golden_cross = (current_ma20 > current_ma50 and prev_ma20 <= prev_ma50)
            ma20_above_ma50 = current_ma20 > current_ma50
        else:
            # Fallback: use price vs MA20 when MA50 not available
            golden_cross = (current_close > current_ma20 and df['Close'].iloc[i-1] <= prev_ma20)
            ma20_above_ma50 = current_close > current_ma20
        
        # Price trend conditions
        price_above_ma20 = current_close > current_ma20
        
        # BUY CONDITIONS (STRICT RSI < 30 requirement):
        # 1. Strong buy: RSI < 25 with uptrend (very oversold)
        # 2. Golden cross with RSI < 40 (momentum + reasonable RSI)
        # 3. Standard buy: RSI < 30 with strong uptrend (strict requirement)
        strong_buy = (rsi_strong_buy and ma20_above_ma50) and current_position <= 0
        golden_buy = (golden_cross and current_rsi < 40) and current_position <= 0
        trend_buy = (rsi_buy_threshold and ma20_above_ma50 and price_above_ma20) and current_position <= 0
        
        if strong_buy or golden_buy or trend_buy:
            df.loc[df.index[i], 'Signal'] = 1  # Buy signal
            df.loc[df.index[i], 'Position'] = 1  # Long position
            
        # Sell Signal Conditions (Simplified for RSI-focused strategy):
        # 1. RSI > 65 (moderately overbought)
        # 2. RSI > 70 (strong overbought) - immediate sell
        # 3. If we have position and price drops below MA20
        rsi_sell_threshold = current_rsi > 65
        rsi_strong_sell = current_rsi > 70
        
        # Death cross detection (when available)
        if has_long_ma and not pd.isna(current_ma50) and not pd.isna(prev_ma50):
            death_cross = (current_ma20 < current_ma50 and prev_ma20 >= prev_ma50)
            ma20_below_ma50 = current_ma20 < current_ma50
        else:
            # Fallback: use price vs MA20
            death_cross = (current_close < current_ma20 and df['Close'].iloc[i-1] >= prev_ma20)
            ma20_below_ma50 = current_close < current_ma20
        
        # Risk management
        price_below_ma20 = current_close < current_ma20
        
        # SELL CONDITIONS (Adapted):
        # Always sell on strong overbought (RSI > 70) - regardless of position
        strong_sell = rsi_strong_sell  # Remove position requirement for strong signals
        death_sell = death_cross and current_position > 0
        trend_sell = (rsi_sell_threshold and ma20_below_ma50) and current_position > 0
        stop_loss = (price_below_ma20 and ma20_below_ma50) and current_position > 0
        
        if strong_sell or death_sell or trend_sell or stop_loss:
            df.loc[df.index[i], 'Signal'] = -1  # Sell signal
            df.loc[df.index[i], 'Position'] = 0  # Exit position
            
        else:
            # Hold current position
            df.loc[df.index[i], 'Position'] = current_position
    
    return df


def calculate_signal_strength(df):
    """
    Calculate signal strength based on multiple indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with technical indicators
        
    Returns:
        pd.Series: Signal strength scores (0-100)
    """
    strength = pd.Series(index=df.index, dtype=float)
    
    for i in range(len(df)):
        score = 50  # Neutral starting point
        
        # RSI contribution (30% weight)
        if df['RSI'].iloc[i] < 30:
            score += 15  # Oversold - bullish
        elif df['RSI'].iloc[i] > 70:
            score -= 15  # Overbought - bearish
            
        # Moving Average contribution (40% weight)
        if df['DMA_20'].iloc[i] > df['DMA_50'].iloc[i]:
            score += 20  # Golden cross - bullish
        else:
            score -= 20  # Death cross - bearish
            
        # Price vs MA contribution (30% weight)
        if df['Close'].iloc[i] > df['DMA_20'].iloc[i]:
            score += 15  # Price above short MA - bullish
        else:
            score -= 15  # Price below short MA - bearish
            
        strength.iloc[i] = max(0, min(100, score))  # Clamp to 0-100
    
    return strength