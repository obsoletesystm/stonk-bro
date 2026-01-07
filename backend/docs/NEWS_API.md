# News & Sentiment Analysis API

The News & Sentiment Analysis API provides comprehensive financial news aggregation and sentiment analysis capabilities using state-of-the-art NLP models.

## Features

- **News Aggregation**: Fetch news from multiple sources (NewsAPI, mock data for testing)
- **Sentiment Analysis**: AI-powered sentiment analysis using FinBERT
- **Historical Tracking**: Daily sentiment aggregation and trend analysis
- **Flexible Querying**: Filter by symbol, sentiment, date range, source
- **Real-time Analysis**: Analyze sentiment of arbitrary text
- **Statistics**: Comprehensive news and sentiment statistics

## Technology Stack

- **Sentiment Model**: ProsusAI/FinBERT (fine-tuned for financial text)
- **NLP Framework**: HuggingFace Transformers
- **News Sources**: NewsAPI (configurable), mock data for testing
- **Database**: PostgreSQL with JSON support for flexible article storage

---

## API Endpoints

### 1. Get News Articles (Paginated)

Retrieve news articles with filtering and pagination.

**Endpoint:** `GET /api/v1/news/articles`

**Query Parameters:**
- `symbols` (optional): Comma-separated stock symbols (e.g., "AAPL,MSFT")
- `sentiment` (optional): Filter by sentiment (`positive`, `neutral`, `negative`)
- `from_date` (optional): Start date (ISO format)
- `to_date` (optional): End date (ISO format)
- `source` (optional): Filter by news source
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 100): Items per page

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/articles?symbols=AAPL,MSFT&page=1&page_size=10"
```

**Example Response:**
```json
{
  "articles": [
    {
      "id": 16,
      "article_id": "60f757b890f6db49ffbc6746d7cf9dc0",
      "source": "newsapi",
      "title": "Apple Beats Q4 Earnings Expectations",
      "description": "Apple Inc. reported strong quarterly results...",
      "url": "https://example.com/article",
      "image_url": "https://example.com/image.jpg",
      "author": "Financial Times",
      "published_at": "2026-01-07T18:50:47.967014",
      "symbols": ["AAPL"],
      "sentiment_score": 0.274,
      "sentiment_label": "positive",
      "sentiment_confidence": 0.837,
      "category": "Business",
      "created_at": "2026-01-07T18:50:47.981754"
    }
  ],
  "total": 125,
  "page": 1,
  "page_size": 10,
  "has_next": true
}
```

---

### 2. Get Recent News

Get recent news articles for a specific symbol.

**Endpoint:** `GET /api/v1/news/{symbol}/recent`

**Path Parameters:**
- `symbol`: Stock symbol (e.g., AAPL)

**Query Parameters:**
- `hours` (default: 24, max: 168): Hours to look back
- `limit` (default: 50, max: 100): Maximum articles to return

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/AAPL/recent?hours=48&limit=20"
```

**Example Response:**
```json
[
  {
    "id": 16,
    "article_id": "60f757b890f6db49ffbc6746d7cf9dc0",
    "source": "newsapi",
    "title": "Apple Announces New Product Launch",
    "description": "Apple unveils new MacBook Pro...",
    "url": "https://example.com/article",
    "published_at": "2026-01-07T14:50:47.967039",
    "symbols": ["AAPL"],
    "sentiment_score": 0.336,
    "sentiment_label": "positive",
    "sentiment_confidence": 0.899
  }
]
```

---

### 3. Get Sentiment Summary

Get comprehensive sentiment analysis summary for a symbol.

**Endpoint:** `GET /api/v1/news/{symbol}/sentiment`

**Path Parameters:**
- `symbol`: Stock symbol (e.g., AAPL)

**Query Parameters:**
- `days` (default: 7, max: 30): Number of days to analyze

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/AAPL/sentiment?days=7"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "period_start": "2025-12-31T18:53:53.776228",
  "period_end": "2026-01-07T18:53:53.776228",
  "avg_sentiment": 0.079,
  "median_sentiment": 0.274,
  "std_sentiment": 0.254,
  "positive_count": 5,
  "neutral_count": 3,
  "negative_count": 2,
  "total_articles": 10,
  "positive_ratio": 0.5,
  "negative_ratio": 0.2,
  "sentiment_trend": "stable",
  "history": [
    {
      "symbol": "AAPL",
      "date": "2026-01-07T00:00:00",
      "avg_sentiment": 0.087,
      "sentiment_std": 0.267,
      "positive_count": 5,
      "neutral_count": 2,
      "negative_count": 2,
      "total_articles": 9,
      "weighted_sentiment": 0.087
    }
  ]
}
```

**Sentiment Trends:**
- `improving`: Sentiment increasing over time (>0.1 change)
- `declining`: Sentiment decreasing over time (<-0.1 change)
- `stable`: Sentiment relatively unchanged

---

### 4. Get Top News by Sentiment

Retrieve top news articles sorted by sentiment score.

**Endpoint:** `GET /api/v1/news/{symbol}/top-news`

**Path Parameters:**
- `symbol`: Stock symbol

**Query Parameters:**
- `sentiment_type` (default: "positive"): `positive` or `negative`
- `limit` (default: 10, max: 50): Number of articles
- `days` (default: 7, max: 30): Days to look back

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/AAPL/top-news?sentiment_type=positive&limit=5"
```

**Example Response:**
```json
[
  {
    "id": 22,
    "article_id": "27c438c32dba2cfc390686a4e7bfc3b6",
    "title": "AAPL maintains steady performance",
    "sentiment_score": 0.336,
    "sentiment_label": "positive",
    "sentiment_confidence": 0.899,
    "sentiment_details": {
      "title": {
        "label": "positive",
        "score": 0.840,
        "normalized_score": 0.840
      },
      "description": {
        "label": "neutral",
        "score": 0.935,
        "normalized_score": 0.0
      }
    },
    "published_at": "2026-01-07T06:50:47.967047",
    "url": "https://example.com/news/aapl/6"
  }
]
```

---

### 5. Fetch News from Sources

Trigger news fetching from external sources.

**Endpoint:** `POST /api/v1/news/fetch`

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT"],
  "query": null,
  "days": 7,
  "analyze_sentiment": true
}
```

**Parameters:**
- `symbols` (optional): List of stock symbols to fetch news for
- `query` (optional): Custom search query
- `days` (default: 7, max: 30): Days of news to fetch
- `analyze_sentiment` (default: true): Whether to analyze sentiment

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/news/fetch" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL"],
    "days": 14,
    "analyze_sentiment": true
  }'
```

**Example Response:**
```json
{
  "articles_fetched": 50,
  "articles_saved": 42,
  "sources_used": ["newsapi"],
  "message": "Successfully fetched and saved 42 articles"
}
```

**Note:** This endpoint processes sentiment analysis in the background for better performance.

---

### 6. Analyze Text Sentiment

Analyze sentiment of arbitrary text.

**Endpoint:** `POST /api/v1/news/analyze`

**Request Body:**
```json
{
  "text": "Apple reports record-breaking quarterly earnings with strong iPhone sales."
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/news/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Stock prices plummet amid economic uncertainty"}'
```

**Example Response:**
```json
{
  "label": "negative",
  "score": 0.892,
  "confidence": 0.892,
  "normalized_score": -0.892,
  "timestamp": "2026-01-07T18:53:33.776228"
}
```

**Sentiment Labels:**
- `positive`: Normalized score > 0.05
- `negative`: Normalized score < -0.05
- `neutral`: Normalized score between -0.05 and 0.05

**Score Ranges:**
- `normalized_score`: -1.0 to 1.0 (negative to positive)
- `confidence`: 0.0 to 1.0 (model confidence)

---

### 7. Get News Statistics

Get aggregated news statistics.

**Endpoint:** `GET /api/v1/news/stats`

**Query Parameters:**
- `symbol` (optional): Filter statistics by symbol

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/stats?symbol=AAPL"
```

**Example Response:**
```json
{
  "total_articles": 10,
  "with_sentiment": 10,
  "by_source": {
    "newsapi": 7,
    "mock": 3
  },
  "by_sentiment": {
    "positive": 5,
    "neutral": 3,
    "negative": 2
  }
}
```

---

## Sentiment Analysis Details

### FinBERT Model

The API uses **ProsusAI/FinBERT**, a BERT model fine-tuned specifically for financial sentiment analysis.

**Model Features:**
- Pre-trained on financial news and reports
- Optimized for financial terminology
- High accuracy on market-related text
- Handles complex financial language

### Weighted Sentiment Scoring

Articles are analyzed using a weighted approach:

```
Final Score = (Title × 0.40) + (Description × 0.35) + (Content × 0.25)
```

**Weights:**
- **Title**: 40% (most informative, concise)
- **Description**: 35% (summary of key points)
- **Content**: 25% (full context, may be truncated)

### Sentiment Normalization

Scores are normalized to a -1.0 to 1.0 scale:
- **Positive**: > 0.05
- **Neutral**: -0.05 to 0.05
- **Negative**: < -0.05

---

## CLI Scripts

### Fetch News Script

Fetch news and analyze sentiment from the command line.

**Location:** `scripts/fetch_news.py`

**Usage:**

```bash
# Fetch news for specific symbols
python scripts/fetch_news.py --symbols AAPL,MSFT,GOOGL

# Fetch news for all portfolio holdings
python scripts/fetch_news.py --from-portfolio

# Fetch 14 days of news
python scripts/fetch_news.py --symbols AAPL --days 14

# Skip sentiment analysis
python scripts/fetch_news.py --symbols AAPL --no-sentiment

# Use NewsAPI (requires API key in .env)
python scripts/fetch_news.py --symbols AAPL --use-newsapi
```

**Docker Usage:**

```bash
# Fetch news in Docker container
docker compose exec api python scripts/fetch_news.py --symbols AAPL,MSFT

# Fetch from portfolio
docker compose exec api python scripts/fetch_news.py --from-portfolio
```

**Output Example:**

```
======================================================================
News Fetching - 2026-01-07 18:50:47.967002
======================================================================
Symbols: AAPL, MSFT
Days: 7
Sentiment Analysis: True

Fetched 50 articles
✓ Saved 42 new articles

Updating sentiment history...
✓ Updated sentiment history for AAPL
✓ Updated sentiment history for MSFT

=== Summary ===
Total articles fetched: 50
New articles saved: 42
Symbols processed: 2

=== Sentiment Summary ===

AAPL:
  Total Articles: 25
  Avg Sentiment: 0.142
  Positive: 15 (60.0%)
  Negative: 4 (16.0%)
  Trend: improving

MSFT:
  Total Articles: 17
  Avg Sentiment: -0.023
  Positive: 7 (41.2%)
  Negative: 5 (29.4%)
  Trend: declining
```

---

## Integration Examples

### Python Integration

```python
import requests
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8000/api/v1/news"

# Get sentiment summary
def get_sentiment(symbol: str, days: int = 7):
    response = requests.get(
        f"{BASE_URL}/{symbol}/sentiment",
        params={"days": days}
    )
    return response.json()

# Get recent news
def get_recent_news(symbol: str, hours: int = 24):
    response = requests.get(
        f"{BASE_URL}/{symbol}/recent",
        params={"hours": hours, "limit": 50}
    )
    return response.json()

# Fetch new articles
def fetch_news(symbols: list):
    response = requests.post(
        f"{BASE_URL}/fetch",
        json={
            "symbols": symbols,
            "days": 7,
            "analyze_sentiment": True
        }
    )
    return response.json()

# Analyze custom text
def analyze_text(text: str):
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": text}
    )
    return response.json()

# Example usage
sentiment = get_sentiment("AAPL", days=7)
print(f"AAPL Sentiment: {sentiment['avg_sentiment']:.3f}")
print(f"Trend: {sentiment['sentiment_trend']}")

# Analyze headline
result = analyze_text("Apple announces record profits")
print(f"Sentiment: {result['label']} ({result['normalized_score']:.3f})")
```

### JavaScript Integration

```javascript
const BASE_URL = 'http://localhost:8000/api/v1/news';

// Get sentiment summary
async function getSentiment(symbol, days = 7) {
  const response = await fetch(
    `${BASE_URL}/${symbol}/sentiment?days=${days}`
  );
  return response.json();
}

// Get paginated articles
async function getArticles(params = {}) {
  const queryParams = new URLSearchParams({
    page: params.page || 1,
    page_size: params.pageSize || 20,
    symbols: params.symbols?.join(',') || '',
    sentiment: params.sentiment || ''
  });

  const response = await fetch(
    `${BASE_URL}/articles?${queryParams}`
  );
  return response.json();
}

// Fetch news
async function fetchNews(symbols, days = 7) {
  const response = await fetch(`${BASE_URL}/fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbols,
      days,
      analyze_sentiment: true
    })
  });
  return response.json();
}

// Example usage
const sentiment = await getSentiment('AAPL', 7);
console.log(`Avg Sentiment: ${sentiment.avg_sentiment.toFixed(3)}`);
console.log(`Positive Ratio: ${(sentiment.positive_ratio * 100).toFixed(1)}%`);

const articles = await getArticles({
  symbols: ['AAPL', 'MSFT'],
  sentiment: 'positive',
  page: 1,
  pageSize: 10
});
console.log(`Found ${articles.total} articles`);
```

---

## Data Models

### NewsArticle

Main news article model with sentiment analysis.

**Fields:**
- `id`: Auto-incrementing primary key
- `article_id`: Unique article identifier (MD5 hash)
- `source`: News source (newsapi, mock, etc.)
- `title`: Article title
- `description`: Article description/summary
- `content`: Full article content
- `url`: Article URL
- `image_url`: Featured image URL
- `author`: Article author
- `published_at`: Publication timestamp
- `symbols`: Array of related stock symbols (JSON)
- `sentiment_score`: Normalized sentiment score (-1 to 1)
- `sentiment_label`: Sentiment category (positive/neutral/negative)
- `sentiment_confidence`: Model confidence (0 to 1)
- `sentiment_details`: Detailed breakdown by component (JSON)
- `category`: Article category
- `keywords`: Article keywords (JSON array)
- `created_at`: Database creation timestamp
- `analyzed_at`: Sentiment analysis timestamp

### SentimentHistory

Daily aggregated sentiment metrics per symbol.

**Fields:**
- `id`: Auto-incrementing primary key
- `symbol`: Stock symbol
- `date`: Date (daily aggregation)
- `avg_sentiment`: Average sentiment score
- `sentiment_std`: Standard deviation of sentiment
- `positive_count`: Number of positive articles
- `neutral_count`: Number of neutral articles
- `negative_count`: Number of negative articles
- `total_articles`: Total articles for the day
- `weighted_sentiment`: Weighted sentiment score
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

---

## Configuration

### Environment Variables

Configure news sources in `.env`:

```bash
# NewsAPI Configuration
NEWS_API_KEY=your_newsapi_key_here

# Sentiment Model Configuration
SENTIMENT_MODEL=ProsusAI/finbert
SENTIMENT_DEVICE=cpu  # or 'cuda' for GPU
```

### NewsAPI Setup

1. Sign up at [newsapi.org](https://newsapi.org/)
2. Get your API key
3. Add to `.env` file:
   ```bash
   NEWS_API_KEY=your_key_here
   ```
4. Use `--use-newsapi` flag when fetching:
   ```bash
   python scripts/fetch_news.py --symbols AAPL --use-newsapi
   ```

### Model Performance

**FinBERT Model:**
- **Size**: ~440MB
- **First Load**: ~10-15 seconds (downloads model)
- **Subsequent Loads**: ~2-3 seconds (cached)
- **Analysis Speed**: ~1-2 seconds per article (CPU)
- **GPU Acceleration**: 5-10x faster with CUDA

**Recommendations:**
- Use GPU for high-volume processing
- Batch process articles for efficiency
- Cache model in production (already implemented)
- Run sentiment analysis in background tasks

---

## Best Practices

### 1. Fetching News

- **Regular Updates**: Fetch news daily or hourly for active symbols
- **Rate Limiting**: Respect NewsAPI rate limits (500 requests/day on free tier)
- **Background Processing**: Use background tasks for large batches
- **Error Handling**: Handle API failures gracefully with retry logic

```python
# Good: Batch fetch for multiple symbols
fetch_news(symbols=["AAPL", "MSFT", "GOOGL"], days=7)

# Avoid: Individual API calls for each symbol
```

### 2. Sentiment Analysis

- **Weighted Analysis**: Use the built-in weighted scoring for best results
- **Context Matters**: Longer text provides better sentiment accuracy
- **Financial Context**: FinBERT understands financial jargon better than general models
- **Batch Processing**: Analyze articles in batches for efficiency

### 3. Querying Articles

- **Pagination**: Always use pagination for large result sets
- **Date Filtering**: Use date ranges to improve query performance
- **Symbol Filtering**: Filter by symbol when possible for faster queries
- **Indexing**: Database indexes on symbols, published_at, sentiment_label

```python
# Efficient query with filters
articles = get_articles(
    symbols=["AAPL"],
    sentiment="positive",
    from_date="2026-01-01",
    page_size=20
)
```

### 4. Performance Optimization

- **Cache Sentiment**: Sentiment scores are cached in the database
- **Background Tasks**: Use FastAPI BackgroundTasks for non-critical operations
- **Model Caching**: Sentiment model is loaded once and reused
- **Database Indexes**: Leverage indexes for symbol and date queries

### 5. Data Quality

- **Deduplication**: Articles are deduplicated by article_id (URL + timestamp hash)
- **Symbol Extraction**: Improve by using NER for better symbol detection
- **Source Diversity**: Fetch from multiple sources for comprehensive coverage
- **Validation**: Validate articles have required fields before saving

---

## Troubleshooting

### Common Issues

**1. Slow Sentiment Analysis**

*Problem:* Sentiment analysis takes too long

*Solutions:*
- Enable GPU if available (set `SENTIMENT_DEVICE=cuda`)
- Process in batches
- Use background tasks
- Consider caching results

**2. NewsAPI Rate Limits**

*Problem:* Hit NewsAPI rate limits (500/day on free tier)

*Solutions:*
- Upgrade to paid plan
- Use mock data for testing
- Cache articles aggressively
- Reduce fetch frequency

**3. Memory Issues with Large Batches**

*Problem:* Out of memory when processing many articles

*Solutions:*
- Process in smaller batches
- Clear model cache between batches
- Use CPU instead of keeping model in GPU memory
- Implement pagination

**4. Inaccurate Sentiment Scores**

*Problem:* Sentiment doesn't match article tone

*Solutions:*
- FinBERT is optimized for financial text
- Check if article is actually financial news
- Review weighted scoring parameters
- Consider fine-tuning model on your specific domain

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check sentiment analysis details:

```bash
# Get detailed sentiment breakdown
curl "http://localhost:8000/api/v1/news/AAPL/top-news?limit=1" | jq '.[] | .sentiment_details'
```

---

## API Response Codes

- **200 OK**: Successful request
- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Symbol or resource not found
- **500 Internal Server Error**: Server error (check logs)

---

## Future Enhancements

Planned improvements:

1. **Additional Sources**: Integration with more news APIs
2. **Real-time Streaming**: WebSocket support for live news feeds
3. **Enhanced NER**: Better symbol extraction using Named Entity Recognition
4. **Multi-language Support**: Sentiment analysis in multiple languages
5. **Sentiment Alerts**: Automated alerts for significant sentiment changes
6. **Market Correlation**: Link sentiment trends with price movements
7. **Custom Models**: Support for custom fine-tuned sentiment models
8. **News Summarization**: AI-powered article summarization

---

## Support & Documentation

- **API Documentation**: Auto-generated at `/docs` (Swagger UI)
- **Alternative Docs**: Available at `/redoc` (ReDoc)
- **Source Code**: See `app/api/v1/endpoints/news.py`
- **Models**: See `app/models/news.py`
- **Services**: See `app/services/news_*.py`

For issues or questions, check the application logs or API documentation.
