# Technical Indicators API Documentation

## Overview

The Technical Indicators API provides comprehensive technical analysis for stocks using pure pandas/numpy calculations. All indicators are calculated using historical OHLCV (Open, High, Low, Close, Volume) data stored in TimescaleDB.

## Base URL

```
http://localhost:8000/api/v1/indicators
```

## Available Indicators

### Moving Averages
- **SMA** (Simple Moving Average) - 20, 50, 200 periods
- **EMA** (Exponential Moving Average) - 12, 26 periods

### Oscillators
- **RSI** (Relative Strength Index) - 14 period
- **Stochastic** - %K and %D lines

### Trend Indicators
- **MACD** (Moving Average Convergence Divergence)
- **ADX** (Average Directional Index) - 14 period
- **ATR** (Average True Range) - 14 period

### Volatility
- **Bollinger Bands** - Upper, Middle (SMA), Lower

### Volume
- **OBV** (On-Balance Volume)

## Endpoints

### 1. Get All Indicators

Get comprehensive technical analysis for a symbol.

**Endpoint:** `GET /api/v1/indicators/{symbol}`

**Parameters:**
- `symbol` (path, required): Stock symbol (e.g., AAPL, MSFT)
- `days` (query, optional): Days of historical data to use (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/AAPL?days=100
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "timestamp": "2026-01-06T17:54:01.547595+00:00",
  "price": {
    "current": 298.14,
    "open": 297.64,
    "high": 300.13,
    "low": 296.16,
    "volume": 6380734
  },
  "moving_averages": {
    "sma_20": 299.98,
    "sma_50": 284.36,
    "sma_200": null,
    "ema_12": 300.18,
    "ema_26": 295.34
  },
  "oscillators": {
    "rsi_14": 49.42,
    "stoch_k": 22.30,
    "stoch_d": 15.45
  },
  "macd": {
    "macd": 4.85,
    "signal": 6.49,
    "histogram": -1.64
  },
  "bollinger_bands": {
    "upper": 310.82,
    "middle": 299.98,
    "lower": 289.14
  },
  "trend": {
    "adx_14": 36.91,
    "atr_14": 5.53
  },
  "volume": {
    "obv": 186155909.0
  },
  "signals": {
    "rsi": "Neutral",
    "macd": "Bearish (MACD < Signal)",
    "bollinger": "Neutral",
    "trend": "Strong trend (ADX > 25)",
    "ma_crossover": "Bullish (20 > 50)"
  },
  "data_points": 99,
  "period_days": 100
}
```

### 2. Get Simple Moving Average (SMA)

**Endpoint:** `GET /api/v1/indicators/{symbol}/sma`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): SMA period (default: 20)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/AAPL/sma?period=50&days=150
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "indicator": "SMA_50",
  "current_value": 284.36,
  "values": [
    {
      "timestamp": "2025-12-08T17:54:01.547595+00:00",
      "value": 280.45
    },
    ...
  ]
}
```

### 3. Get Exponential Moving Average (EMA)

**Endpoint:** `GET /api/v1/indicators/{symbol}/ema`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): EMA period (default: 20)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/MSFT/ema?period=12
```

### 4. Get RSI (Relative Strength Index)

**Endpoint:** `GET /api/v1/indicators/{symbol}/rsi`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): RSI period (default: 14)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/GOOGL/rsi
```

**Example Response:**
```json
{
  "symbol": "GOOGL",
  "indicator": "RSI_14",
  "current_value": 52.34,
  "signal": "Neutral",
  "values": [
    {
      "timestamp": "2025-12-08T17:54:01.547595+00:00",
      "value": 45.32
    },
    ...
  ]
}
```

**RSI Signals:**
- `Overbought (>70)`: RSI > 70
- `Oversold (<30)`: RSI < 30
- `Neutral`: RSI between 30 and 70

### 5. Get MACD

**Endpoint:** `GET /api/v1/indicators/{symbol}/macd`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `fast` (query, optional): Fast EMA period (default: 12)
- `slow` (query, optional): Slow EMA period (default: 26)
- `signal` (query, optional): Signal line period (default: 9)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/TSLA/macd
```

**Example Response:**
```json
{
  "symbol": "TSLA",
  "indicator": "MACD(12,26,9)",
  "current_values": {
    "macd": 3.78,
    "signal": 4.05,
    "histogram": -0.27
  },
  "signal": "Bearish (MACD < Signal)",
  "values": [
    {
      "timestamp": "2025-12-08T17:54:01.547595+00:00",
      "macd": -6.03,
      "signal": -3.30,
      "histogram": -2.73
    },
    ...
  ]
}
```

**MACD Signals:**
- `Bullish (MACD > Signal)`: MACD line above signal line
- `Bearish (MACD < Signal)`: MACD line below signal line

### 6. Get Bollinger Bands

**Endpoint:** `GET /api/v1/indicators/{symbol}/bollinger`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): SMA period (default: 20)
- `std` (query, optional): Standard deviation multiplier (default: 2)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/NVDA/bollinger?period=20&std=2
```

**Example Response:**
```json
{
  "symbol": "NVDA",
  "indicator": "BB(20,2)",
  "current_price": 447.94,
  "current_values": {
    "upper": 550.45,
    "middle": 522.59,
    "lower": 494.73
  },
  "signal": "Neutral",
  "values": [
    {
      "timestamp": "2025-12-08T17:54:01.547595+00:00",
      "upper": 590.45,
      "middle": 562.48,
      "lower": 534.51
    },
    ...
  ]
}
```

**Bollinger Band Signals:**
- `Price at upper band (overbought)`: Price >= Upper band
- `Price at lower band (oversold)`: Price <= Lower band
- `Neutral`: Price between bands

### 7. Get Stochastic Oscillator

**Endpoint:** `GET /api/v1/indicators/{symbol}/stochastic`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `k_period` (query, optional): %K period (default: 14)
- `d_period` (query, optional): %D period (default: 3)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/AAPL/stochastic
```

### 8. Get ATR (Average True Range)

**Endpoint:** `GET /api/v1/indicators/{symbol}/atr`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): ATR period (default: 14)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/MSFT/atr
```

### 9. Get ADX (Average Directional Index)

**Endpoint:** `GET /api/v1/indicators/{symbol}/adx`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `period` (query, optional): ADX period (default: 14)
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/GOOGL/adx
```

**ADX Signals:**
- `Strong trend (ADX > 25)`: ADX > 25
- `Weak trend (ADX < 20)`: ADX < 20
- `Moderate trend`: ADX between 20 and 25

### 10. Get OBV (On-Balance Volume)

**Endpoint:** `GET /api/v1/indicators/{symbol}/obv`

**Parameters:**
- `symbol` (path, required): Stock symbol
- `days` (query, optional): Days of historical data (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/api/v1/indicators/TSLA/obv
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "No historical data found"
}
```

Returned when:
- Symbol doesn't exist in the database
- No historical data available for the requested period

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "period"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

Returned when:
- Invalid parameter types
- Missing required parameters

## CLI Script

A command-line script is available for batch indicator calculation:

```bash
# Calculate for specific symbols
python scripts/calculate_indicators.py --symbols AAPL,MSFT,GOOGL --days 100

# Calculate for all portfolio holdings
python scripts/calculate_indicators.py --from-portfolio --days 200
```

**Output Example:**
```
============================================================
Technical Analysis: AAPL
============================================================
Timestamp: 2026-01-06T17:54:01.547595+00:00
Data Points: 99 (100 days)

Current Price: $298.14
  Open: $297.64 | High: $300.13 | Low: $296.16
  Volume: 6,380,734

Moving Averages:
  SMA(20):  $299.98
  SMA(50):  $284.36
  SMA(200): None
  EMA(12):  $300.18
  EMA(26):  $295.34

Oscillators:
  RSI(14):       49.42
  Stochastic %K: 22.30
  Stochastic %D: 15.45

MACD:
  MACD:      4.8464
  Signal:    6.4882
  Histogram: -1.6417

Bollinger Bands:
  Upper:  $310.82
  Middle: $299.98
  Lower:  $289.14

Trend Indicators:
  ADX(14): 36.91
  ATR(14): $5.53

Volume Indicators:
  OBV: 186,155,909

Trading Signals:
  RSI: Neutral
  MACD: Bearish (MACD < Signal)
  BOLLINGER: Neutral
  TREND: Strong trend (ADX > 25)
  MA_CROSSOVER: Bullish (20 > 50)
```

## Implementation Details

### Technology Stack
- **Calculation Engine**: Pure pandas and numpy (no external TA libraries)
- **Database**: TimescaleDB (PostgreSQL with time-series extensions)
- **API Framework**: FastAPI with Pydantic v2 schemas
- **Performance**: Efficient bulk calculations using pandas vectorization

### Calculation Methods

All indicators are implemented using standard formulas:

- **SMA**: `df['close'].rolling(window=period).mean()`
- **EMA**: `df['close'].ewm(span=period, adjust=False).mean()`
- **RSI**: Standard gain/loss ratio method with 14-period default
- **MACD**: EMA(12) - EMA(26) with 9-period signal line
- **Bollinger Bands**: SMA ± (std_dev * multiplier)
- **Stochastic**: (Close - Low_min) / (High_max - Low_min) * 100
- **ATR**: Rolling mean of true range (max of high-low, |high-close[t-1]|, |low-close[t-1]|)
- **ADX**: Directional movement index with smoothing
- **OBV**: Cumulative volume based on price direction

### Data Requirements

- Minimum data points vary by indicator:
  - SMA/EMA: Requires at least `period` days
  - RSI: Requires at least `period + 1` days
  - MACD: Requires at least `slow_period` days (26 default)
  - Bollinger Bands: Requires at least `period` days
  - ATR/ADX: Requires at least `period * 2` days

### Trading Signals

The API provides automatic signal interpretation:

1. **RSI Signals**: Overbought (>70), Oversold (<30), Neutral
2. **MACD Signals**: Bullish/Bearish crossover
3. **Bollinger Bands**: Price at upper/lower band or neutral
4. **ADX Signals**: Strong/Weak/Moderate trend strength
5. **MA Crossover**: SMA(20) vs SMA(50) comparison

## Best Practices

1. **Data Period Selection**:
   - Use at least 100 days for reliable SMA/EMA calculations
   - Use 200+ days for SMA(200) calculation
   - Longer periods provide more stable indicators but less responsiveness

2. **Combining Indicators**:
   - Use trend (MACD, ADX) with momentum (RSI, Stochastic) indicators
   - Confirm signals across multiple indicators
   - Consider volume (OBV) for validation

3. **Error Handling**:
   - Check for null values in responses (insufficient data)
   - Handle 404 errors for symbols without data
   - Validate parameter ranges

4. **Performance**:
   - Cache results for frequently accessed symbols
   - Use appropriate `days` parameter to balance accuracy and speed
   - Consider batch processing with CLI script for multiple symbols

## Examples

### Python Example
```python
import requests

# Get comprehensive indicators
response = requests.get('http://localhost:8000/api/v1/indicators/AAPL?days=100')
data = response.json()

print(f"Current Price: ${data['price']['current']}")
print(f"RSI: {data['oscillators']['rsi_14']:.2f}")
print(f"Signal: {data['signals']['rsi']}")

# Get specific indicator
rsi_response = requests.get('http://localhost:8000/api/v1/indicators/AAPL/rsi')
rsi_data = rsi_response.json()
print(f"RSI: {rsi_data['current_value']:.2f} - {rsi_data['signal']}")
```

### JavaScript Example
```javascript
// Get all indicators
fetch('http://localhost:8000/api/v1/indicators/AAPL?days=100')
  .then(response => response.json())
  .then(data => {
    console.log(`Current Price: $${data.price.current}`);
    console.log(`RSI: ${data.oscillators.rsi_14.toFixed(2)}`);
    console.log(`Signal: ${data.signals.rsi}`);
  });

// Get MACD
fetch('http://localhost:8000/api/v1/indicators/AAPL/macd')
  .then(response => response.json())
  .then(data => {
    console.log(`MACD: ${data.current_values.macd.toFixed(2)}`);
    console.log(`Signal: ${data.signal}`);
  });
```

### cURL Examples
```bash
# Get all indicators with custom period
curl "http://localhost:8000/api/v1/indicators/AAPL?days=200"

# Get RSI with custom period
curl "http://localhost:8000/api/v1/indicators/MSFT/rsi?period=21&days=100"

# Get MACD with custom parameters
curl "http://localhost:8000/api/v1/indicators/GOOGL/macd?fast=8&slow=21&signal=5"

# Get Bollinger Bands with 3 standard deviations
curl "http://localhost:8000/api/v1/indicators/TSLA/bollinger?period=20&std=3"
```

## Testing

Test data can be generated using the test data script:

```bash
python scripts/generate_test_data.py
```

This creates 250 days of realistic mock data for AAPL, MSFT, GOOGL, TSLA, and NVDA.

## Future Enhancements

Potential additions:
- [ ] Fibonacci retracement levels
- [ ] Ichimoku Cloud
- [ ] Volume-weighted indicators (VWAP)
- [ ] Custom indicator combinations
- [ ] Historical backtesting support
- [ ] Real-time indicator updates via WebSocket
- [ ] Indicator alerts and notifications
