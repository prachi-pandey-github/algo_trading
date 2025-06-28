"""
Backtesting module for strategy performance evaluation.

This module implements:
- Historical trade simulation
- Performance metrics calculation (win rate, total return, etc.)
- Risk management evaluation
- Trade logging and analysis
"""

import pandas as pd
from config import settings


def backtest_strategy(df, initial_capital=None):
    """
    Backtest the trading strategy on historical data.
    
    Args:
        df (pd.DataFrame): DataFrame with signals and market data
        initial_capital (float): Starting capital amount
        
    Returns:
        tuple: (trades_list, total_return, win_rate, trade_count)
    """
    if initial_capital is None:
        initial_capital = settings.INITIAL_CAPITAL
    
    position = 0
    trades = []
    capital = initial_capital
    trade_count = 0
    win_count = 0
    buy_price = 0
    
    for date, row in df.iterrows():
        # Buy signal execution
        if row['Signal'] == 1 and position == 0:
            position = capital // row['Close']
            buy_price = row['Close']
            capital -= position * buy_price
            
            trades.append({
                'Timestamp': date, 
                'Type': 'BUY', 
                'Price': buy_price,
                'Quantity': position,
                'RSI': row.get('RSI', 0),
                'DMA_20': row.get('DMA_20', 0),
                'DMA_50': row.get('DMA_50', 0),
                'MACD': row.get('MACD', 0),
                'Volume_Ratio': row.get('Volume_Ratio', 1)
            })
        
        # Sell signal execution
        elif row['Signal'] == -1 and position > 0:
            sell_price = row['Close']
            trade_value = position * sell_price
            capital += trade_value
            
            # Calculate profit/loss
            pnl = (sell_price - buy_price) * position
            
            trades.append({
                'Timestamp': date,
                'Type': 'SELL',
                'Price': sell_price,
                'Quantity': position,
                'PnL': pnl,
                'RSI': row.get('RSI', 0),
                'DMA_20': row.get('DMA_20', 0),
                'DMA_50': row.get('DMA_50', 0),
                'MACD': row.get('MACD', 0),
                'Volume_Ratio': row.get('Volume_Ratio', 1)
            })
            
            # Update statistics
            if pnl > 0:
                win_count += 1
            trade_count += 1
            position = 0
    
    # Close any remaining position at the end
    if position > 0:
        final_price = df['Close'].iloc[-1]
        trade_value = position * final_price
        capital += trade_value
        
        pnl = (final_price - buy_price) * position
        trades.append({
            'Timestamp': df.index[-1],
            'Type': 'SELL',
            'Price': final_price,
            'Quantity': position,
            'PnL': pnl,
            'RSI': df['RSI'].iloc[-1] if 'RSI' in df.columns else 0,
            'DMA_20': df['DMA_20'].iloc[-1] if 'DMA_20' in df.columns else 0,
            'DMA_50': df['DMA_50'].iloc[-1] if 'DMA_50' in df.columns else 0,
            'MACD': df['MACD'].iloc[-1] if 'MACD' in df.columns else 0,
            'Volume_Ratio': df['Volume_Ratio'].iloc[-1] if 'Volume_Ratio' in df.columns else 1
        })
        
        if pnl > 0:
            win_count += 1
        trade_count += 1
    
    # Calculate performance metrics
    total_return = (capital - initial_capital) / initial_capital
    win_rate = win_count / trade_count if trade_count > 0 else 0
    
    return trades, total_return, win_rate, trade_count