# 🚀 NIFTY 50 Algorithmic Trading System

A comprehensive algorithmic trading system for NIFTY 50 stocks with machine learning integration, technical analysis, and Telegram notifications.

## ✨ Features

- **📊 NIFTY 50 Stock Analysis**: Automated trading for top Indian stocks
- **🔄 Real-time Data**: Live market data fetching via Yahoo Finance
- **📈 Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands
- **🤖 Machine Learning**: Multiple ML models (Decision Tree, Random Forest, Logistic Regression)
- **📱 Telegram Integration**: Live trading alerts and daily summaries
- **📊 Backtesting**: Historical performance evaluation
- **💾 Data Logging**: Comprehensive CSV export for analysis

## 🏗️ System Architecture

```
algo_trading_system/
├── main.py              # Main trading system orchestrator
├── demo.py              # Demo script for testing
├── requirements.txt     # Python dependencies
├── config/             
│   ├── settings.py      # Trading parameters & stock tickers
│   └── api_keys.py      # API credentials (create this)
├── modules/
│   ├── data_loader.py   # Market data fetching & technical indicators
│   ├── strategy_engine.py # Trading strategy implementation
│   ├── backtester.py    # Performance evaluation
│   ├── ml_predictor.py  # Machine learning models
│   ├── csv_writer.py    # Data logging & export
│   └── telegram_bot.py  # Notification system
└── data/
    └── outputs/         # Generated reports and logs
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/algo_trading_system.git
cd algo_trading_system

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the API keys template and configure:
```bash
cp config/api_keys_template.py config/api_keys.py
```

Edit `config/api_keys.py` with your credentials:
```python
# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
```

### 3. Run Demo

```bash
# Test the system with demo data
python demo.py
```

### 4. Full System Execution

```bash
# Run the complete trading system
python main.py
```

## 📊 Trading Strategy

### Entry Signals (BUY)
- RSI < 30 (oversold condition)
- 20-day MA crosses above 50-day MA (golden cross)

### Exit Signals (SELL)
- RSI > 70 (overbought condition)
- 20-day MA crosses below 50-day MA (death cross)

### Machine Learning Enhancement
- Predicts next-day price movement
- Uses multiple models for robust predictions
- Provides confidence scores for trade decisions

## 📈 Supported Stocks (NIFTY 50)

- RELIANCE.NS, TCS.NS, HDFCBANK.NS
- INFY.NS, HINDUNILVR.NS, ICICIBANK.NS
- KOTAKBANK.NS, BHARTIARTL.NS, ITC.NS
- SBIN.NS, LT.NS, WIPRO.NS, MARUTI.NS
- And more...

## 📱 Telegram Alerts

Example trading alert format:
```
🚨 TRADING ALERT 🚨
📊 Ticker: RELIANCE.NS
📈 Action: BUY
💰 Price: $1450.50
📉 RSI: 28.5
🕐 Time: 2025-06-29 15:30:00
🎯 ML Confidence: 65.2%
```

## 📊 Output Files

- `data/outputs/trade_log.csv` - All trade details
- `data/outputs/ml_results.csv` - ML model performance
- `data/outputs/summary.csv` - Overall system performance

## 🔧 Customization

### Adding New Stocks
Edit `config/settings.py`:
```python
TICKERS = [
    "RELIANCE.NS",
    "YOUR_STOCK.NS"  # Add new stocks here
]
```

### Modifying Strategy
Edit `modules/strategy_engine.py` to customize:
- Entry/exit conditions
- Risk management rules
- Position sizing

### ML Models
Edit `modules/ml_predictor.py` to:
- Add new features
- Try different algorithms
- Adjust hyperparameters

## 📋 Requirements

- Python 3.8+
- Internet connection for live data
- Telegram bot



## 📈 Performance Metrics

The system tracks:
- Total return percentage
- Win rate (profitable trades %)
- Number of trades executed
- ML model accuracy scores
- Risk-adjusted returns















