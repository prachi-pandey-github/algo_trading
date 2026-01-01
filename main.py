from config import settings
from modules import (
    data_loader,
    strategy_engine,
    backtester,
    csv_writer,
    ml_predictor,
    telegram_bot
)

from datetime import datetime
from modules.google_sheets_logger import GoogleSheetsLogger
from config.google_sheets import GOOGLE_CREDS_PATH, GOOGLE_SHEET_NAME


def main():
    """
    Main function to run the algorithmic trading system.
    
    This function orchestrates the entire trading pipeline:
    1. Data fetching and technical analysis
    2. Trading strategy execution
    3. Backtesting and performance evaluation
    4. Machine learning model training
    5. Results logging and Telegram notifications
    """
    print("Starting Algorithmic Trading System")
    print("=" * 50)
    

    # Initialize system components
    csv_writer.initialize_csv_files()
    telegram_bot.send_startup_message()

    # Initialize Google Sheets logger
    print("\nInitializing Google Sheets connection...")
    try:
        sheets_logger = GoogleSheetsLogger(GOOGLE_CREDS_PATH, GOOGLE_SHEET_NAME)
        print("Successfully connected to Google Sheets")
    except Exception as e:
        print(f"Error connecting to Google Sheets: {str(e)}")
        print("Please check that:")
        print("1. The sheet name matches exactly: 'Algo Trading'")
        print("2. The service account email has Editor access to the sheet:")
        print("   sheets-access-service@thematic-nature-455407-t7.iam.gserviceaccount.com")
        return

    all_summaries = []
    
    for ticker in settings.TICKERS:
        print(f"\nProcessing {ticker}...")
        
        try:
            # 1. Data Ingestion and Technical Analysis
            df = data_loader.fetch_stock_data(ticker, settings.DATA_RANGE, settings.INTERVAL)
            df = data_loader.calculate_technical_indicators(df)
            
            if df.empty:
                print(f"No data available for {ticker}, skipping...")
                continue
            
            # 2. Strategy Execution
            df = strategy_engine.generate_signals(df)
            
            # 3. Backtesting
            trades, total_return, win_rate, trade_count = backtester.backtest_strategy(df)
            
            # 4. Trade Logging

            for trade in trades:
                trade_data = {
                    'Timestamp': trade['Timestamp'],
                    'Ticker': ticker,
                    'Signal': trade['Type'],
                    'Price': trade['Price'],
                    'Quantity': trade.get('Quantity', 0),
                    'PnL': trade.get('PnL', 0),
                    'RSI': trade.get('RSI', 0),
                    'DMA_20': trade.get('DMA_20', 0),
                    'DMA_50': trade.get('DMA_50', 0),
                    'MACD': trade.get('MACD', 0),
                    'Volume_Ratio': trade.get('Volume_Ratio', 1)
                }
                csv_writer.log_trade(trade_data)
                # Log to Google Sheets (Trade Log tab)
                sheets_logger.log_trade([
                    trade_data['Timestamp'], trade_data['Ticker'], trade_data['Signal'],
                    trade_data['Price'], trade_data['Quantity'], trade_data['PnL']
                ])
            
            # 5. Machine Learning Model Training
            best_accuracy = train_ml_models(ticker, df)
            
            # 6. Performance Summary

            summary_data = {
                'Ticker': ticker,
                'StartDate': df.index[0].date(),
                'EndDate': df.index[-1].date(),
                'InitialCapital': settings.INITIAL_CAPITAL,
                'FinalValue': settings.INITIAL_CAPITAL * (1 + total_return),
                'ReturnPct': total_return * 100,
                'WinRate': win_rate * 100,
                'TotalTrades': trade_count
            }
            all_summaries.append(summary_data)
            # Log summary P&L to Google Sheets (Summary P&L tab)
            sheets_logger.log_summary([
                str(datetime.now().date()), summary_data['FinalValue']
            ])
            # Log win ratio to Google Sheets (Win Ratio tab)
            sheets_logger.log_win_ratio([
                str(datetime.now().date()), summary_data['WinRate']
            ])
            
            # 7. Trading Alerts
            send_trading_alerts(ticker, trades, best_accuracy)
            
            print(f"✅ Completed processing {ticker}")
            
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            continue
    
    # Final system summary and cleanup
    finalize_system(all_summaries)


def train_ml_models(ticker, df):
    """Train and evaluate multiple ML models for the given ticker."""
    ml_df = ml_predictor.prepare_features(df.copy())
    print(f"  🤖 Training Decision Tree model...")
    
    try:
        ml_result = ml_predictor.train_model(ml_df, model_type="decision_tree")
        
        if len(ml_result) == 4:
            model, scaler, accuracy, class_report = ml_result
            if model is not None:
                best_accuracy = accuracy
                print(f"    Decision Tree accuracy: {accuracy:.3f}")
            
    except Exception as e:
        print(f"    Decision Tree: Failed - {e}")
        best_accuracy = 0
    
    # Log ML results
    if best_accuracy > 0:
        csv_writer.log_ml_results({
            'Timestamp': datetime.now(),
            'Ticker': ticker,
            'Accuracy': best_accuracy,
            'Features': "Model: Decision Tree, RSI, MACD, Volume, BB, MA"
        })
        print(f"  ✅ ML model accuracy: {best_accuracy:.2%}")
    else:
        print(f"  ⚠️ ML training failed for {ticker}")
    
    return best_accuracy


def send_trading_alerts(ticker, trades, ml_accuracy):
    """Send trading alerts for the most recent trades."""
    if trades:
        print(f"  📈 Found {len(trades)} trades")
        
        # Send alert for the most recent trade
        latest_trade = trades[-1]
        if latest_trade['Type'] in ['BUY', 'SELL']:
            print(f"  📱 Sending alert: {latest_trade['Type']} at ${latest_trade['Price']:.2f}")
            
            success = telegram_bot.send_trading_signal(
                ticker=ticker,
                signal_type=latest_trade['Type'],
                price=latest_trade['Price'],
                rsi=latest_trade.get('RSI', 50),
                confidence=ml_accuracy if ml_accuracy > 0.6 else None
            )
            
            if success:
                print(f"  ✅ Alert sent successfully")
            else:
                print(f"  ❌ Failed to send alert")
    else:
        print(f"  📊 No trades found")


def finalize_system(all_summaries):
    """Complete system processing and send final summary."""
    print("\n" + "=" * 50)
    print("📋 Finalizing System Results...")
    

    # Save summaries
    for summary in all_summaries:
        csv_writer.log_summary(summary)
        # Optionally, could log again to Google Sheets here if needed
    
    # Send daily summary
    if all_summaries:
        telegram_bot.send_daily_summary(all_summaries)
        print("✅ Daily summary sent to Telegram")
    
    print("🎯 Processing complete! Check data/outputs for detailed results.")
    print("=" * 50)

if __name__ == "__main__":
    main()