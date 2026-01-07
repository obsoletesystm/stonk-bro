# Machine Learning API Documentation

## Overview

The ML API provides stock price prediction capabilities using trained machine learning models. The system supports both XGBoost (gradient boosting) and LSTM (deep learning) models for predicting future stock returns, prices, or price direction.

## Base URL

```
http://localhost:8000/api/v1/ml
```

## Features

- **Multiple Model Types**: XGBoost and LSTM
- **Multiple Prediction Targets**: Returns, absolute price, or direction (up/down)
- **Multi-Horizon Predictions**: 1, 5, 10, 20+ day forecasts
- **Feature Engineering**: 77+ technical and statistical features
- **Model Versioning**: Automatic model storage with metadata
- **Backtesting**: Evaluate strategies based on predictions
- **Feature Importance**: Understand which features drive predictions

## Endpoints

### 1. Make Prediction

Get a price prediction for a stock.

**Endpoint:** `GET /api/v1/ml/{symbol}/predict`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `model_type` (query, optional): Model type - 'xgboost' or 'lstm' (default: 'xgboost')
- `target_type` (query, optional): Prediction type - 'returns', 'price', or 'direction' (default: 'returns')
- `horizon` (query, optional): Days ahead to predict (default: 1)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/AAPL/predict?model_type=xgboost&horizon=1"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "model_type": "xgboost",
  "target_type": "returns",
  "horizon": 1,
  "current_price": 297.30,
  "prediction": 0.006336,
  "predicted_price": 299.18,
  "predicted_return": 0.634,
  "direction": "UP",
  "timestamp": "2026-01-07T18:16:21.096466",
  "model_metadata": {
    "trained_at": "20260107_181604",
    "test_rmse": 0.014177,
    "test_r2": 0.0724
  }
}
```

### 2. Multi-Horizon Predictions

Get predictions for multiple time horizons.

**Endpoint:** `GET /api/v1/ml/{symbol}/predict/multi-horizon`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `model_type` (query, optional): Model type (default: 'xgboost')
- `target_type` (query, optional): Prediction type (default: 'returns')

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/AAPL/predict/multi-horizon"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "model_type": "xgboost",
  "target_type": "returns",
  "predictions": {
    "1d": {
      "predicted_price": 299.18,
      "predicted_return": 0.63,
      "direction": "UP",
      "horizon": 1
    },
    "5d": {
      "predicted_price": 311.25,
      "predicted_return": 0.47,
      "direction": "UP",
      "horizon": 5
    },
    "10d": {
      "predicted_price": 300.07,
      "predicted_return": 0.39,
      "direction": "UP",
      "horizon": 10
    },
    "20d": {
      "predicted_price": 289.56,
      "predicted_return": 0.46,
      "direction": "UP",
      "horizon": 20
    }
  },
  "timestamp": "2026-01-07T18:16:15.830830"
}
```

### 3. List Available Models

Get information about trained models for a symbol.

**Endpoint:** `GET /api/v1/ml/{symbol}/models`

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/AAPL/models"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "models_available": 2,
  "models": [
    {
      "model_type": "xgboost",
      "target_type": "returns",
      "horizon": 1,
      "trained_at": "20260107_181604",
      "test_rmse": 0.014177,
      "test_r2": 0.0724,
      "n_features": 77
    },
    {
      "model_type": "lstm",
      "target_type": "returns",
      "horizon": 5,
      "trained_at": "20260107_120000",
      "test_rmse": 0.022345,
      "test_r2": 0.1523,
      "n_features": 77
    }
  ]
}
```

### 4. Train Model

Train a new ML model for a stock.

**Endpoint:** `POST /api/v1/ml/{symbol}/train`

**Request Body:**
```json
{
  "symbol": "AAPL",
  "model_type": "xgboost",
  "target_type": "returns",
  "horizon": 1,
  "days": 500
}
```

**Parameters:**
- `symbol` (string, required): Stock symbol
- `model_type` (string): 'xgboost' or 'lstm' (default: 'xgboost')
- `target_type` (string): 'returns', 'price', or 'direction' (default: 'returns')
- `horizon` (integer): Days ahead to predict, 1-30 (default: 1)
- `days` (integer): Days of historical data, 100-2000 (default: 500)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ml/AAPL/train" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "model_type": "xgboost", "target_type": "returns", "horizon": 1, "days": 500}'
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "model_type": "xgboost",
  "test_metrics": {
    "mse": 0.000201,
    "rmse": 0.014177,
    "mae": 0.011004,
    "r2": 0.0724,
    "direction_accuracy": 0.60
  },
  "n_features": 77,
  "model_path": "/app/ml/artifacts/AAPL_xgboost_returns_20260107_181604.pkl",
  "message": "Model trained successfully for AAPL"
}
```

### 5. Backtest Model

Run backtesting on trained model predictions.

**Endpoint:** `POST /api/v1/ml/{symbol}/backtest`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `model_type` (query): Model type (default: 'xgboost')
- `target_type` (query): Target type (default: 'returns')
- `horizon` (query): Prediction horizon (default: 1)
- `strategy` (query): Trading strategy - 'simple' or 'threshold' (default: 'simple')
- `threshold` (query): Strategy threshold (default: 0.0)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ml/AAPL/backtest?strategy=simple&threshold=0.0"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "strategy": "simple",
  "strategy_params": {
    "threshold": 0.0
  },
  "metrics": {
    "total_return": 0.0523,
    "buy_hold_return": 0.0412,
    "excess_return": 0.0111,
    "annualized_return": 0.2545,
    "volatility": 0.1876,
    "sharpe_ratio": 1.3567,
    "max_drawdown": -0.0823,
    "calmar_ratio": 3.0924,
    "win_rate": 0.5234,
    "avg_win": 0.0142,
    "avg_loss": -0.0098,
    "profit_factor": 1.4521,
    "total_trades": 23,
    "n_days": 100
  },
  "message": "Backtest completed successfully"
}
```

### 6. Get Feature Importance

Get feature importance for XGBoost models.

**Endpoint:** `GET /api/v1/ml/{symbol}/feature-importance`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `model_type` (query): Model type (must be 'xgboost')
- `target_type` (query): Target type (default: 'returns')
- `top_n` (query): Number of top features (default: 20)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/AAPL/feature-importance?top_n=10"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "model_type": "xgboost",
  "top_features": [
    {
      "feature": "obv_ma_ratio",
      "importance": 0.0755
    },
    {
      "feature": "macd_histogram_lag_1",
      "importance": 0.0594
    },
    {
      "feature": "rsi_14_lag_3",
      "importance": 0.0533
    },
    {
      "feature": "bb_width",
      "importance": 0.0516
    },
    {
      "feature": "macd",
      "importance": 0.0485
    }
  ]
}
```

## CLI Scripts

### Train Models

Train models from the command line:

```bash
# Train single symbol
python scripts/train_model.py --symbol AAPL --model xgboost

# Train multiple symbols
python scripts/train_model.py --symbols AAPL,MSFT,GOOGL --model xgboost --horizon 5

# Train from portfolio
python scripts/train_model.py --from-portfolio --model lstm --target returns

# Custom parameters
python scripts/train_model.py --symbol AAPL --model xgboost \
  --learning-rate 0.01 --n-estimators 1000 --max-depth 7
```

**Output:**
```
======================================================================
ML Model Training - 2026-01-07 18:16:04.726905
======================================================================
Model Type: xgboost
Target Type: returns
Horizon: 1 day(s)
Training 1 symbol(s)

[1/1] Training AAPL...

======================================================================
Training Results: AAPL
======================================================================
Model Type: xgboost
Features: 77
Model saved to: /app/ml/artifacts/AAPL_xgboost_returns_20260107_181604.pkl

Test Metrics:
  RMSE:      0.014177
  MAE:       0.011004
  R² Score:  0.0724
  Direction: 60.00%
```

### Make Predictions

Make predictions from the command line:

```bash
# Single prediction
python scripts/predict_price.py --symbol AAPL

# Multi-horizon prediction
python scripts/predict_price.py --symbol AAPL --multi-horizon

# Multiple symbols
python scripts/predict_price.py --symbols AAPL,MSFT,GOOGL --model xgboost
```

**Output:**
```
======================================================================
Multi-Horizon Predictions: AAPL
======================================================================
Model: xgboost (returns)
Timestamp: 2026-01-07T18:16:15.830830

1D      : $299.18 (+0.63%) [UP]
5D      : $311.25 (+0.47%) [UP]
10D     : $300.07 (+0.39%) [UP]
20D     : $289.56 (+0.46%) [UP]
```

## Feature Engineering

The ML models use 77+ engineered features across multiple categories:

### Price Features
- Returns (simple and log returns)
- Price changes and percentage changes
- High-Low spread
- Open-Close spread
- Price position in daily range

### Momentum Features
- Rate of Change (ROC) for 1, 5, 10, 20 periods
- Momentum indicators
- Williams %R

### Volatility Features
- Historical volatility (5, 10, 20, 30 periods)
- Parkinson's volatility
- ATR percentage

### Technical Indicators
- Moving Averages: SMA (5, 10, 20, 50, 200), EMA (12, 26, 50)
- RSI (14-period)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2σ)
- Stochastic Oscillator
- ADX (trend strength)
- OBV (volume)

### Lagged Features
- Lagged values (1, 2, 3, 5 periods) for:
  - Close price
  - Volume
  - Returns
  - RSI
  - MACD histogram

## Model Types

### XGBoost

Gradient boosting model ideal for:
- Feature importance analysis
- Fast training and inference
- Robust to outliers
- Good interpretability

**Parameters:**
- `n_estimators`: 1000 (default)
- `max_depth`: 7 (default)
- `learning_rate`: 0.01 (default)
- `subsample`: 0.8
- `colsample_bytree`: 0.8

### LSTM

Deep learning model ideal for:
- Capturing temporal patterns
- Long-term dependencies
- Complex non-linear relationships

**Parameters:**
- `hidden_size`: 128 (default)
- `num_layers`: 2 (default)
- `sequence_length`: 60
- `dropout`: 0.2
- `learning_rate`: 0.001
- `epochs`: 100 (default)

## Target Types

### Returns
Predicts percentage price change:
- Most common for short-term trading
- Easy to compare across stocks
- Handles different price scales

### Price
Predicts absolute future price:
- Direct price forecast
- Useful for specific price targets
- May struggle with scaling

### Direction
Binary classification (up/down):
- Simplified prediction task
- Focus on direction accuracy
- Good for simple trading strategies

## Backtesting

The backtesting framework evaluates trading strategies based on ML predictions:

### Strategies

**Simple Strategy:**
- Buy when predicted return > threshold
- Hold when in position

**Threshold Strategy:**
- Buy when prediction > buy_threshold
- Sell when prediction < sell_threshold
- Maintains position otherwise

### Metrics

- **Total Return**: Overall strategy return
- **Excess Return**: Strategy return vs buy-and-hold
- **Sharpe Ratio**: Risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: Return / max drawdown
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss

## Best Practices

### Model Training

1. **Data Requirements**:
   - Minimum 100 days for meaningful training
   - 250+ days recommended for robust models
   - 500+ days for long-term predictions

2. **Feature Selection**:
   - Use feature importance to identify key drivers
   - Remove highly correlated features
   - Consider domain knowledge

3. **Validation**:
   - Use time-series cross-validation
   - Evaluate on out-of-sample data
   - Monitor R² and direction accuracy

4. **Retraining**:
   - Retrain models periodically (monthly/quarterly)
   - Monitor performance degradation
   - Update when market conditions change

### Making Predictions

1. **Model Selection**:
   - XGBoost for short-term (1-5 days)
   - LSTM for longer-term (5-20 days)
   - Ensemble both for robust predictions

2. **Interpretation**:
   - Check model metadata (R², RMSE)
   - Consider confidence/uncertainty
   - Don't rely on single prediction

3. **Risk Management**:
   - Use predictions as one input
   - Combine with other analysis
   - Set stop-losses and position sizes

## Error Responses

### 404 Not Found
```json
{
  "detail": "No xgboost model found for AAPL with target_type=returns"
}
```

### 400 Bad Request
```json
{
  "detail": "Feature importance only available for XGBoost models"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error training model: Insufficient data"
}
```

## Performance Notes

- **Training Time**:
  - XGBoost: 5-30 seconds
  - LSTM: 2-10 minutes

- **Prediction Time**:
  - XGBoost: <100ms
  - LSTM: <500ms

- **Memory Usage**:
  - XGBoost model: ~10-50 MB
  - LSTM model: ~50-200 MB

## Examples

### Python
```python
import requests

# Train model
train_response = requests.post(
    'http://localhost:8000/api/v1/ml/AAPL/train',
    json={
        'symbol': 'AAPL',
        'model_type': 'xgboost',
        'target_type': 'returns',
        'horizon': 1,
        'days': 500
    }
)
print(train_response.json())

# Make prediction
pred_response = requests.get(
    'http://localhost:8000/api/v1/ml/AAPL/predict',
    params={'model_type': 'xgboost', 'horizon': 1}
)
prediction = pred_response.json()
print(f"Predicted return: {prediction['predicted_return']:.2f}%")
print(f"Direction: {prediction['direction']}")

# Get feature importance
importance_response = requests.get(
    'http://localhost:8000/api/v1/ml/AAPL/feature-importance',
    params={'top_n': 10}
)
features = importance_response.json()
for f in features['top_features']:
    print(f"{f['feature']}: {f['importance']:.4f}")
```

### JavaScript
```javascript
// Make prediction
fetch('http://localhost:8000/api/v1/ml/AAPL/predict?model_type=xgboost&horizon=1')
  .then(response => response.json())
  .then(data => {
    console.log(`Current: $${data.current_price}`);
    console.log(`Predicted: $${data.predicted_price}`);
    console.log(`Return: ${data.predicted_return.toFixed(2)}%`);
    console.log(`Direction: ${data.direction}`);
  });

// Multi-horizon predictions
fetch('http://localhost:8000/api/v1/ml/AAPL/predict/multi-horizon')
  .then(response => response.json())
  .then(data => {
    Object.entries(data.predictions).forEach(([horizon, pred]) => {
      console.log(`${horizon}: $${pred.predicted_price} (${pred.predicted_return.toFixed(2)}%)`);
    });
  });
```

## Future Enhancements

- [ ] Ensemble models (combine XGBoost + LSTM)
- [ ] Additional model types (Random Forest, Prophet)
- [ ] Confidence intervals / prediction intervals
- [ ] Model performance monitoring dashboard
- [ ] Automated retraining scheduler
- [ ] Multi-stock portfolio optimization
- [ ] Sentiment-enhanced predictions
- [ ] Options pricing models
