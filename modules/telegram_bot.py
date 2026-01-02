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
            result = response.json()
            if result.get('ok'):
                print(f"Telegram alert sent successfully")
                return True
            else:
                print(f"Telegram API error: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"Failed to send Telegram alert: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data.get('description', response.text)}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error sending Telegram alert: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending Telegram alert: {e}")
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
    
    message = f"""TRADING ALERT
Ticker: {ticker}
Action: {signal_display}
Price: ₹{price:.2f}
RSI: {rsi:.1f}
Time: {timestamp}"""
    
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
        message = "<b>DAILY TRADING SUMMARY</b>\n\n"
        
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
<b>OVERALL PERFORMANCE</b>
   Avg Return: {avg_return:.2f}%
   Total Trades: {total_trades}
   Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return send_telegram_alert(message)
        
    except Exception as e:
        print(f"Error sending daily summary: {e}")
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

<b>Ticker:</b> {ticker}
<b>Accuracy:</b> {accuracy:.2%}
<b>Features:</b> {features}
<b>Trained:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
    Test the Telegram bot connection and configuration.
    
    Returns:
        bool: True if connection successful
    """
    try:
        # Check if credentials are configured
        if not hasattr(api_keys, 'TELEGRAM_BOT_TOKEN') or not api_keys.TELEGRAM_BOT_TOKEN:
            print("TELEGRAM_BOT_TOKEN not configured")
            return False
            
        if not hasattr(api_keys, 'TELEGRAM_CHAT_ID') or not api_keys.TELEGRAM_CHAT_ID:
            print("❌ TELEGRAM_CHAT_ID not configured")
            return False
            
        if api_keys.TELEGRAM_BOT_TOKEN == "your_actual_bot_token_here":
            print("❌ Please replace placeholder bot token with actual token")
            return False
            
        if api_keys.TELEGRAM_CHAT_ID == "your_actual_chat_id_here":
            print("❌ Please replace placeholder chat ID with actual chat ID")
            return False
        
        # Test bot info endpoint
        url = f"https://api.telegram.org/bot{api_keys.TELEGRAM_BOT_TOKEN}/getMe"
        print(f"🔍 Testing bot connection: {url[:50]}...")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info.get('result', {}).get('username', 'Unknown')
                print(f"✅ Bot connection successful: @{bot_name}")
                
                # Test sending a simple message
                test_message = "🤖 Telegram bot connection test successful!"
                test_url = f"https://api.telegram.org/bot{api_keys.TELEGRAM_BOT_TOKEN}/sendMessage"
                test_payload = {
                    'chat_id': api_keys.TELEGRAM_CHAT_ID,
                    'text': test_message
                }
                test_response = requests.post(test_url, data=test_payload, timeout=10)
                
                if test_response.status_code == 200:
                    print("✅ Test message sent successfully")
                    return True
                else:
                    print(f"❌ Test message failed: {test_response.status_code}")
                    print(f"Response: {test_response.text}")
                    return False
            else:
                print(f"❌ Bot API returned error: {bot_info.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ Bot connection failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Telegram connection: {e}")
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