# Stocks Table and Associations

## Overview

The `stocks` table provides a normalized reference for all identified stock tickers. It enables efficient querying, deduplication, and enrichment with company metadata.

## Schema

### stocks table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `symbol` | VARCHAR(10) | Stock ticker symbol (unique, indexed) |
| `company_name` | VARCHAR(255) | Full company name |
| `sector` | VARCHAR(100) | Industry sector |
| `exchange` | VARCHAR(50) | Stock exchange (NASDAQ, NYSE, TSX, etc.) |
| `is_active` | BOOLEAN | Whether stock is actively traded |
| `last_updated` | TIMESTAMP | Last metadata update |
| `created_at` | TIMESTAMP | When stock was first added |

**Indexes:**
- `idx_stocks_symbol` on `symbol`

**Constraints:**
- `UNIQUE` on `symbol`

### content_stock_mentions table (Junction)

Links raw content to mentioned stocks (many-to-many relationship).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Primary key |
| `content_id` | BIGINT | FK to raw_content.id |
| `stock_id` | INTEGER | FK to stocks.id |
| `mention_type` | VARCHAR(20) | How stock was mentioned (cashtag, company_name, inferred) |
| `confidence` | FLOAT | Confidence score (0.0-1.0) for fuzzy matches |
| `created_at` | TIMESTAMP | When association was created |

**Indexes:**
- `idx_content_stock_mentions_content` on `content_id`
- `idx_content_stock_mentions_stock` on `stock_id`
- `idx_content_stock_mentions_unique` on `(content_id, stock_id)` UNIQUE

**Foreign Keys:**
- `content_id` → `raw_content.id` (CASCADE DELETE)
- `stock_id` → `stocks.id` (CASCADE DELETE)

## Usage Examples

### 1. Create/Get Stock

```python
from app.models.sentiment import Stock
from app.core.db import SessionLocal

db = SessionLocal()

# Check if stock exists
stock = db.query(Stock).filter(Stock.symbol == 'AAPL').first()

if not stock:
    # Create new stock
    stock = Stock(
        symbol='AAPL',
        company_name='Apple Inc.',
        sector='Technology',
        exchange='NASDAQ',
        is_active=True
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)

print(f"Stock ID: {stock.id}, Symbol: {stock.symbol}")
```

### 2. Associate Content with Stock

```python
from app.models.sentiment import ContentStockMention

# After identifying stocks in content
mention = ContentStockMention(
    content_id=content.id,
    stock_id=stock.id,
    mention_type='cashtag',  # 'cashtag', 'company_name', or 'inferred'
    confidence=1.0
)
db.add(mention)
db.commit()
```

### 3. Query Stocks Mentioned in Content

```python
from sqlalchemy.orm import joinedload

# Get all stocks mentioned in a specific piece of content
content = db.query(RawContent).filter(
    RawContent.id == content_id
).first()

# Query through junction table
mentions = db.query(ContentStockMention).filter(
    ContentStockMention.content_id == content_id
).all()

for mention in mentions:
    stock = db.query(Stock).filter(Stock.id == mention.stock_id).first()
    print(f"{stock.symbol} - {mention.mention_type} (confidence: {mention.confidence})")
```

### 4. Get All Content for a Stock

```python
# Find all content mentioning AAPL
stock = db.query(Stock).filter(Stock.symbol == 'AAPL').first()

mentions = db.query(ContentStockMention).filter(
    ContentStockMention.stock_id == stock.id
).all()

for mention in mentions:
    content = db.query(RawContent).filter(
        RawContent.id == mention.content_id
    ).first()
    print(f"Content: {content.title} (from {content.source})")
```

### 5. Bulk Insert Stocks

```python
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']

for symbol in symbols:
    existing = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not existing:
        stock = Stock(symbol=symbol, is_active=True)
        db.add(stock)

db.commit()
```

## Integration with Stock Identifier Service

The Stock Identifier service (to be implemented in S-008 and S-009) will:

1. Extract ticker symbols from raw content
2. Create or retrieve Stock records
3. Create ContentStockMention associations
4. Enrich Stock records with yfinance data

Example flow:
```
Raw Content → Ticker Extraction → Stock Creation/Lookup → Association
```

## Best Practices

1. **Always check for existing stocks before creating**
   - Use `symbol` as the unique identifier
   - Prevents duplicates

2. **Use appropriate mention_type**
   - `cashtag`: Extracted from $SYMBOL format
   - `company_name`: Matched from company name
   - `inferred`: Detected through context/NLP

3. **Set confidence scores**
   - 1.0 for exact cashtag matches
   - 0.8-0.99 for fuzzy company name matches
   - 0.5-0.79 for contextual inferences

4. **Keep metadata updated**
   - Periodically refresh `company_name`, `sector`, `exchange` from yfinance
   - Set `is_active=False` for delisted stocks

5. **Leverage indexes**
   - Query by `symbol` (indexed)
   - Join through `content_stock_mentions` for content-stock relationships

## Testing

Run the validation script:
```bash
python test_stocks_schema.py
```

This tests:
- Table existence
- Schema correctness
- CRUD operations
- Associations
- Unique constraints

## Migration

The stocks tables were created in migration:
```
backend/alembic/versions/20260121224647_add_sentiment_raw_content_tables.py
```

To apply:
```bash
alembic upgrade head
```

To verify:
```sql
\d stocks
\d content_stock_mentions
```
