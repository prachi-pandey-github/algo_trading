"""
Trading strategy engine module.

This module implements:
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
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data and technical indicators
        
    Returns:
        pd.DataFrame: DataFrame with added signal columns
    """
    print("\nAnalyzing trading conditions...")
    signal_count = 0
    
    # Initialize signal columns
    df['Signal'] = 0  # 0 = Hold, 1 = Buy, -1 = Sell
    df['Position'] = 0  # Track current position
    df['Entry_Price'] = 0.0  # Track entry prices for positions
    
    # Check if we have enough data for long-term MA
    has_long_ma = not df['DMA_50'].isna().all()
    
    # Practical Strategy Implementation
    for i in range(1, len(df)):
        current_position = df['Position'].iloc[i-1] if i > 0 else 0
        
        # Get current values
        current_rsi = df['RSI'].iloc[i]
        current_ma20 = df['DMA_20'].iloc[i]
        current_ma50 = df['DMA_50'].iloc[i] if not pd.isna(df['DMA_50'].iloc[i]) else current_ma20
        current_close = df['Close'].iloc[i]
        
        # Previous values for cross detection
        prev_ma20 = df['DMA_20'].iloc[i-1] if i > 0 else current_ma20
        prev_ma50 = df['DMA_50'].iloc[i-1] if i > 0 and not pd.isna(df['DMA_50'].iloc[i-1]) else prev_ma20
        
        # Calculate volume confirmation
        volume_ma = df['Volume'].rolling(20).mean().iloc[i]
        volume_confirmation = df['Volume'].iloc[i] > volume_ma
        
        # Buy Signal Conditions
        buy_signal = (
            current_rsi < 40 and  # More lenient RSI threshold
            (
                # Either MA crossover
                (prev_ma20 <= prev_ma50 and current_ma20 > current_ma50) or
                # Or strong RSI condition
                (current_rsi < 30)
            ) and
            volume_confirmation and  # Add volume confirmation
            current_position <= 0  # Not already in a position
        )
        
        # Sell Signal Conditions
        rsi_overbought = current_rsi > 70
        stop_loss_triggered = current_close < current_ma20 * 0.95  # 5% below MA20
        profit_target_hit = current_position > 0 and current_close >= df['Entry_Price'].iloc[i-1] * 1.1  # 10% profit target
        
        # Death cross detection
        death_cross = False
        if has_long_ma and not pd.isna(current_ma50) and not pd.isna(prev_ma50):
            death_cross = (current_ma20 < current_ma50 and prev_ma20 >= prev_ma50)
        
        # Combined sell conditions
        sell_signal = (
            (rsi_overbought or  # Overbought condition
            stop_loss_triggered or  # Stop loss
            profit_target_hit or  # Profit target
            death_cross) and  # Technical pattern
            current_position > 0  # Must have a position to sell
        )
        
        # Signal generation and position management
        if buy_signal:
            df.loc[df.index[i], 'Signal'] = 1  # Buy signal
            df.loc[df.index[i], 'Position'] = 1  # Long position
            df.loc[df.index[i], 'Entry_Price'] = current_close
            signal_count += 1
            print(f"  BUY signal generated at {df.index[i].date()}: RSI={current_rsi:.1f}, MA20={current_ma20:.2f}, MA50={current_ma50:.2f}, Volume_Conf={volume_confirmation}")
        
        elif sell_signal:
            df.loc[df.index[i], 'Signal'] = -1  # Sell signal
            df.loc[df.index[i], 'Position'] = 0  # Exit position
            df.loc[df.index[i], 'Entry_Price'] = 0.0
            signal_count += 1
            
            # Get the reason for the sell
            sell_reason = "RSI Overbought" if rsi_overbought else \
                         "Stop Loss" if stop_loss_triggered else \
                         "Profit Target" if profit_target_hit else \
                         "Death Cross"
            
            print(f"  SELL signal generated at {df.index[i].date()}: {sell_reason}, Price={current_close:.2f}")
        
        else:
            # Hold current position and entry price
            df.loc[df.index[i], 'Position'] = current_position
            df.loc[df.index[i], 'Entry_Price'] = df['Entry_Price'].iloc[i-1] if i > 0 else 0.0
    
    print(f"\nStrategy analysis complete. Generated {signal_count} signals.")
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
        if not pd.isna(df['DMA_50'].iloc[i]):
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