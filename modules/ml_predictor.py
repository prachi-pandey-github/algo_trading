"""
Machine Learning prediction module.

This module implements:
- Feature engineering for stock market data
- Multiple ML model training (Decision Tree, Logistic Regression, Random Forest)
- Model evaluation and selection
- Prediction accuracy assessment
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


def prepare_features(df):
    """
    Prepare features for machine learning model with enhanced technical indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with technical indicators and signals
        
    Returns:
        pd.DataFrame: DataFrame with prepared features and target variable
    """
    # Create a copy to avoid modifying original data
    ml_df = df.copy()
    
    # Create target variable (next period's signal)
    # 1 if price will go up, 0 if price will go down or stay same
    ml_df['Target'] = (ml_df['Close'].shift(-1) > ml_df['Close']).astype(int)
    
    # Create additional features
    ml_df['Price_Change'] = ml_df['Close'].pct_change()
    ml_df['Volume_Change'] = ml_df['Volume'].pct_change()
    
    # RSI-based features
    ml_df['RSI_Oversold'] = (ml_df['RSI'] < 30).astype(int)
    ml_df['RSI_Overbought'] = (ml_df['RSI'] > 70).astype(int)
    ml_df['RSI_Change'] = ml_df['RSI'].diff()
    
    # Moving Average features
    ml_df['MA_Cross'] = (ml_df['DMA_20'] > ml_df['DMA_50']).astype(int)
    ml_df['Price_Above_MA20'] = (ml_df['Close'] > ml_df['DMA_20']).astype(int)
    ml_df['Price_Above_MA50'] = (ml_df['Close'] > ml_df['DMA_50']).astype(int)
    
    # MACD features
    ml_df['MACD_Bullish'] = (ml_df['MACD'] > ml_df['MACD_Signal']).astype(int)
    ml_df['MACD_Cross_Up'] = ((ml_df['MACD'] > ml_df['MACD_Signal']) & 
                             (ml_df['MACD'].shift(1) <= ml_df['MACD_Signal'].shift(1))).astype(int)
    ml_df['MACD_Cross_Down'] = ((ml_df['MACD'] < ml_df['MACD_Signal']) & 
                               (ml_df['MACD'].shift(1) >= ml_df['MACD_Signal'].shift(1))).astype(int)
    ml_df['MACD_Histogram_Positive'] = (ml_df['MACD_Histogram'] > 0).astype(int)
    
    # Volume features
    ml_df['High_Volume'] = (ml_df['Volume_Ratio'] > 1.5).astype(int)
    ml_df['Low_Volume'] = (ml_df['Volume_Ratio'] < 0.5).astype(int)
    
    # Bollinger Bands features
    ml_df['BB_Position'] = (ml_df['Close'] - ml_df['BB_Lower']) / (ml_df['BB_Upper'] - ml_df['BB_Lower'])
    ml_df['BB_Squeeze'] = ((ml_df['BB_Upper'] - ml_df['BB_Lower']) / ml_df['BB_Middle']).rolling(10).min()
    ml_df['Near_BB_Upper'] = (ml_df['Close'] > ml_df['BB_Upper'] * 0.98).astype(int)
    ml_df['Near_BB_Lower'] = (ml_df['Close'] < ml_df['BB_Lower'] * 1.02).astype(int)
    
    # Volatility features
    ml_df['High_Low_Ratio'] = ml_df['High'] / ml_df['Low']
    ml_df['Close_Open_Ratio'] = ml_df['Close'] / ml_df['Open']
    ml_df['Price_Volatility'] = ml_df['Close'].rolling(5).std()
    
    # Momentum features
    ml_df['Price_MA20_Ratio'] = ml_df['Close'] / ml_df['DMA_20']
    ml_df['Price_MA50_Ratio'] = ml_df['Close'] / ml_df['DMA_50']
    ml_df['Momentum_5'] = ml_df['Close'] / ml_df['Close'].shift(5)
    ml_df['Momentum_10'] = ml_df['Close'] / ml_df['Close'].shift(10)
    
    # Lag features (previous period values)
    ml_df['RSI_Lag1'] = ml_df['RSI'].shift(1)
    ml_df['MACD_Lag1'] = ml_df['MACD'].shift(1)
    ml_df['Volume_Lag1'] = ml_df['Volume_Ratio'].shift(1)
    ml_df['Price_Change_Lag1'] = ml_df['Price_Change'].shift(1)
    
    # Remove rows with NaN values
    ml_df = ml_df.dropna()
    
    return ml_df


def train_model(ml_df, model_type=None):
    """
    Train a Decision Tree model to predict price direction.
    
    Args:
        ml_df (pd.DataFrame): DataFrame with prepared features
        model_type (str): Ignored parameter, kept for backward compatibility
        
    Returns:
        tuple: (trained_model, scaler, accuracy_score, classification_report)
    """
    if len(ml_df) < 50:  # Not enough data for training
        return None, None, 0.0, "Insufficient data"
    
    # Define feature columns (enhanced with MACD, Volume, BB features)
    feature_columns = [
        'RSI', 'DMA_20', 'DMA_50', 'Volume', 'MACD', 'MACD_Signal', 'MACD_Histogram',
        'Price_Change', 'Volume_Change', 'Volume_Ratio',
        'RSI_Oversold', 'RSI_Overbought', 'RSI_Change',
        'MA_Cross', 'Price_Above_MA20', 'Price_Above_MA50',
        'MACD_Bullish', 'MACD_Cross_Up', 'MACD_Cross_Down', 'MACD_Histogram_Positive',
        'High_Volume', 'Low_Volume',
        'BB_Position', 'BB_Squeeze', 'Near_BB_Upper', 'Near_BB_Lower',
        'High_Low_Ratio', 'Close_Open_Ratio', 'Price_Volatility',
        'Price_MA20_Ratio', 'Price_MA50_Ratio', 'Momentum_5', 'Momentum_10',
        'RSI_Lag1', 'MACD_Lag1', 'Volume_Lag1', 'Price_Change_Lag1'
    ]
    
    # Filter only available columns
    available_features = [col for col in feature_columns if col in ml_df.columns]
    
    # Prepare features and target
    X = ml_df[available_features]
    y = ml_df['Target']
    
    # Comprehensive data cleaning for ML models
    # 1. Replace infinity values with NaN
    X = X.replace([np.inf, -np.inf], np.nan)
    
    # 2. Fill NaN values with mean (or 0 for ratios/indicators)
    for col in X.columns:
        if X[col].dtype in ['float64', 'float32']:
            if col.endswith('_Ratio') or col.startswith('Price_'):
                X[col] = X[col].fillna(1.0)  # Default ratio to 1.0
            elif col.startswith('RSI') or col.startswith('MACD'):
                X[col] = X[col].fillna(50.0)  # Default RSI to neutral 50
            else:
                X[col] = X[col].fillna(X[col].mean())
        else:
            X[col] = X[col].fillna(0)  # Binary indicators to 0
    
    # 3. Final check for any remaining problematic values
    X = X.replace([np.inf, -np.inf], 0)
    
    # 4. Ensure we have enough data and variation
    if len(X) < 10:
        return None, None, 0.0, "Insufficient data for ML training"
    
    if y.nunique() < 2:
        return None, None, 0.0, "No variation in target variable"
    
    try:
        # Split the data
        test_size = min(0.3, max(0.1, 100 / len(X)))  # Adaptive test size
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features with robust scaler handling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Additional check for scaling issues
        if np.any(np.isnan(X_train_scaled)) or np.any(np.isinf(X_train_scaled)):
            print(f"Warning: Scaling issues detected for {model_type}")
            return None, None, 0.0, "Scaling failed"
        
        # Train Decision Tree model
        model = DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        # Decision trees don't require scaling, use original data
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        return model, scaler, accuracy, class_report
        
    except Exception as e:
        print(f"Error training {model_type} model: {e}")
        return None, None, 0.0, f"Training failed: {str(e)}"


def predict_next_signal(model, scaler, current_data):
    """
    Predict the next trading signal using the trained model.
    
    Args:
        model: Trained ML model
        scaler: Fitted StandardScaler
        current_data (pd.Series): Current market data
        
    Returns:
        int: Predicted signal (1 for buy, 0 for sell/hold)
    """
    if model is None:
        return 0
    
    try:
        # Prepare features for prediction
        features = np.array([[
            current_data.get('RSI', 50),
            current_data.get('DMA_20', 0),
            current_data.get('DMA_50', 0),
            current_data.get('Volume', 0),
            current_data.get('Price_Change', 0),
            current_data.get('Volume_Change', 0),
            current_data.get('RSI_Oversold', 0),
            current_data.get('RSI_Overbought', 0),
            current_data.get('RSI_Change', 0),
            current_data.get('MA_Cross', 0),
            current_data.get('Price_Above_MA20', 0),
            current_data.get('Price_Above_MA50', 0),
            current_data.get('High_Low_Ratio', 1),
            current_data.get('Close_Open_Ratio', 1),
            current_data.get('Price_MA20_Ratio', 1),
            current_data.get('Price_MA50_Ratio', 1),
            current_data.get('RSI_Lag1', 50),
            current_data.get('Price_Change_Lag1', 0)
        ]])
        
        # Scale features and make prediction
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        
        return prediction
    except Exception as e:
        print(f"Error in prediction: {e}")
        return 0


def get_feature_importance(model, feature_names=None):
    """
    Get feature importance from the trained model.
    
    Args:
        model: Trained ML model
        feature_names (list): Names of features
        
    Returns:
        pd.DataFrame: Feature importance scores
    """
    if model is None or not hasattr(model, 'feature_importances_'):
        return pd.DataFrame()
    
    if feature_names is None:
        feature_names = [
            'RSI', 'DMA_20', 'DMA_50', 'Volume',
            'Price_Change', 'Volume_Change',
            'RSI_Oversold', 'RSI_Overbought', 'RSI_Change',
            'MA_Cross', 'Price_Above_MA20', 'Price_Above_MA50',
            'High_Low_Ratio', 'Close_Open_Ratio',
            'Price_MA20_Ratio', 'Price_MA50_Ratio',
            'RSI_Lag1', 'Price_Change_Lag1'
        ]
    
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    return importance_df