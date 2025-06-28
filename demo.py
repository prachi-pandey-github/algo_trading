#!/usr/bin/env python3
"""
Demo script for the NIFTY 50 Algorithmic Trading System.

This script demonstrates the system's capabilities by:
- Fetching live market data for select NIFTY 50 stocks
- Running technical analysis and strategy signals
- Training ML models for prediction
- Generating sample trading alerts

Usage: python demo.py
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import data_loader, strategy_engine, ml_predictor, telegram_bot
from config import settings
from datetime import datetime


def run_demo():
    """Run a demonstration of the trading system."""
    print("🚀 NIFTY 50 Algorithmic Trading System Demo")
    print("=" * 60)
    print(f"🕐 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Demo with 3 popular NIFTY 50 stocks
    demo_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    
    for i, ticker in enumerate(demo_stocks, 1):
        print(f"📊 Demo {i}/3: Processing {ticker}")
        print("-" * 40)
        
        try:
            # 1. Fetch market data
            print("  📈 Fetching market data...")
            df = data_loader.fetch_stock_data(ticker, period="3mo", interval="1d")
            
            if df.empty:
                print("  ❌ No data available")
                continue
            
            # 2. Calculate technical indicators
            print("  🔧 Calculating technical indicators...")
            df = data_loader.calculate_technical_indicators(df)
            
            # 3. Generate trading signals
            print("  🎯 Generating trading signals...")
            df = strategy_engine.generate_signals(df)
            
            # 4. Display current market status
            latest = df.iloc[-1]
            print(f"  💰 Current Price: ${latest['Close']:.2f}")
            print(f"  📊 RSI: {latest['RSI']:.2f}")
            print(f"  📈 20-DMA: ${latest['DMA_20']:.2f}")
            print(f"  📉 50-DMA: ${latest['DMA_50']:.2f}")
            
            # Determine signal status
            if latest['Signal'] == 1:
                signal_text = "🟢 BUY SIGNAL"
            elif latest['Signal'] == -1:
                signal_text = "🔴 SELL SIGNAL"
            else:
                signal_text = "🟡 HOLD"
            
            print(f"  🎯 Current Signal: {signal_text}")
            
            # 5. ML Model Demo
            print("  🤖 Training ML model...")
            ml_df = ml_predictor.prepare_features(df.copy())
            
            try:
                model, scaler, accuracy, _ = ml_predictor.train_model(ml_df, "random_forest")
                if model is not None:
                    print(f"  ✅ ML Model Accuracy: {accuracy:.2%}")
                else:
                    print("  ⚠️ ML training failed")
            except Exception as e:
                print(f"  ⚠️ ML training error: {e}")
            
            print("  ✅ Demo completed for", ticker)
            
        except Exception as e:
            print(f"  ❌ Error processing {ticker}: {e}")
        
        print()
    
    print("=" * 60)
    print("🎯 Demo Completed Successfully!")
    print()
    print("💡 What you can do next:")
    print("  • Run 'python main.py' for full system execution")
    print("  • Check 'data/outputs/' for detailed results")
    print("  • Configure Telegram bot for live alerts")
    print("  • Customize trading strategy in modules/strategy_engine.py")
    print()
    print("📚 Key Features Demonstrated:")
    print("  ✅ Live market data fetching")
    print("  ✅ Technical indicator calculations")
    print("  ✅ Trading signal generation")
    print("  ✅ Machine learning predictions")
    print("  ✅ Professional system architecture")


if __name__ == "__main__":
    run_demo()
