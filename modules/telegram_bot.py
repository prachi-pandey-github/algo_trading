"""
Telegram bot integration module.

This module handles:
- Trading signal alerts via Telegram
- Daily trading summaries
- ML model performance notifications
- System status messages
"""

import requests
import json
from datetime import datetime
from config import api_keys
import time


def send_telegram_alert(message, parse_mode="HTML"):
    """
    Send a trading alert to Telegram.
    
    Args:
        message (str): The message to send
        parse_mode (str): Message formatting mode ("HTML" or "Markdown")
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Telegram Bot API URL
        url = f"https://api.telegram.org/bot{api_keys.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Prepare the payload
        payload = {
            'chat_id': api_keys.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': parse_mode
        }
        
        # Send the request
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram alert sent successfully")
            return True
        else:
            print(f"❌ Failed to send Telegram alert: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error sending Telegram alert: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending Telegram alert: {e}")
        return False


def send_trading_signal(ticker, signal_type, price, rsi, confidence=None):
    """
    Send a formatted trading signal alert.
    
    Args:
        ticker (str): Stock ticker symbol
        signal_type (str): "BUY", "SELL", "Buy", or "Sell"
        price (float): Current stock price
        rsi (float): Current RSI value
        confidence (float): ML model confidence (optional)
        
    Returns:
        bool: True if sent successfully
    """
    # Normalize signal type - remove emojis, use clear text
    signal_upper = signal_type.upper()
    if signal_upper in ["BUY", "LONG"]:
        signal_display = "BUY"
    elif signal_upper in ["SELL", "SHORT"]:
        signal_display = "SELL"
    else:
        signal_display = signal_upper
    
    # Format the message exactly as requested
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""🚨 TRADING ALERT 🚨
📊 Ticker: {ticker}
📈 Action: {signal_display}
💰 Price: ${price:.2f}
📉 RSI: {rsi:.1f}
🕐 Time: {timestamp}"""
    
    if confidence is not None:
        message += f"\n🎯 ML Confidence: {confidence:.1%}"
    
    return send_telegram_alert(message)


def send_daily_summary(summaries):
    """
    Send a daily trading summary with all ticker results.
    
    Args:
        summaries (list): List of summary dictionaries
        
    Returns:
        bool: True if sent successfully
    """
    try:
        message = "📊 <b>DAILY TRADING SUMMARY</b> 📊\n\n"
        
        total_return = 0
        total_trades = 0
        
        for summary in summaries:
            ticker = summary['Ticker']
            return_pct = summary['ReturnPct']
            win_rate = summary['WinRate']
            trades = summary['TotalTrades']
            
            total_return += return_pct
            total_trades += trades
            
            # Determine performance status with clear text
            if return_pct > 0:
                status = "PROFIT"
            elif return_pct < 0:
                status = "LOSS"
            else:
                status = "NO TRADES"
            
            message += f"""
<b>{ticker}</b> - {status}
   Return: {return_pct:.2f}%
   Win Rate: {win_rate:.1f}%
   Trades: {trades}
"""
        
        # Add overall summary
        avg_return = total_return / len(summaries) if summaries else 0
        message += f"""
━━━━━━━━━━━━━━━━━━━━
📈 <b>OVERALL PERFORMANCE</b>
   Avg Return: {avg_return:.2f}%
   Total Trades: {total_trades}
   Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return send_telegram_alert(message)
        
    except Exception as e:
        print(f"❌ Error sending daily summary: {e}")
        return False


def send_ml_results(ticker, accuracy, features):
    """
    Send ML model training results.
    
    Args:
        ticker (str): Stock ticker
        accuracy (float): Model accuracy score
        features (str): Features used in the model
        
    Returns:
        bool: True if sent successfully
    """
    message = f"""
🤖 <b>ML MODEL UPDATE</b> 🤖

📊 <b>Ticker:</b> {ticker}
🎯 <b>Accuracy:</b> {accuracy:.2%}
🔧 <b>Features:</b> {features}
🕐 <b>Trained:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return send_telegram_alert(message)


def send_error_alert(error_message, context=""):
    """
    Send an error alert to Telegram.
    
    Args:
        error_message (str): The error message
        context (str): Additional context about where the error occurred
        
    Returns:
        bool: True if sent successfully
    """
    message = f"""
⚠️ <b>SYSTEM ERROR</b> ⚠️

🚨 <b>Error:</b> {error_message}
📍 <b>Context:</b> {context}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return send_telegram_alert(message)


def test_telegram_connection():
    """
    Test the Telegram bot connection.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        test_message = f"""
🔧 <b>BOT TEST</b> 🔧

✅ Telegram bot is working correctly!
🕐 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 Trading system is ready to send alerts.
"""
        
        return send_telegram_alert(test_message)
        
    except Exception as e:
        print(f"❌ Telegram connection test failed: {e}")
        return False


def send_startup_message():
    """
    Send a message when the trading system starts up.
    
    Returns:
        bool: True if sent successfully
    """
    message = f"""
🚀 <b>TRADING SYSTEM STARTED</b> 🚀

✅ System initialized successfully
📊 Ready to monitor trading signals
🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Good luck with your trades! 📈💰
"""
    
    return send_telegram_alert(message)