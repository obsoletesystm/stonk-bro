# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal automated stock research and prediction platform for managing a Canadian TFSA investment portfolio. It combines real-time market data analysis, fundamental research, technical indicators, and machine learning-based predictions to support informed investment decisions.

**Critical Context:** This is a single-user, self-hosted platform designed for personal use on a dedicated bare-metal server. All architectural decisions optimize for simplicity, reliability, and cost-efficiency rather than multi-user scalability.

**Hardware:** Dedicated Intel Xeon E3-1240 v5 server (4C/8T, 32GB RAM, 500GB storage, NVIDIA M2000, Ubuntu 24.04)

## Core Architecture Decisions

### Deployment Strategy

**Production Deployment (Recommended):**
- **Primary: Docker Compose**
  - Single machine = Docker Compose is the right tool
  - All services defined in `docker-compose.yml`
  - Simple, reliable, easy to understand and debug
  - Full access to server resources (no orchestration overhead)
  - Managed by systemd for auto-start on boot
  - Host cron jobs for scheduled tasks (simpler than Celery Beat)
  - Direct GPU access for ML training (`--gpus all`)

**Why Not Kubernetes?**
- Single dedicated machine doesn't need orchestration
- k8s adds complexity without benefits for this use case
- Docker Compose uses ~1-2% overhead vs k8s ~5-10%
- Simpler debugging, monitoring, and maintenance
- You already know k8s - no learning value here

**Advanced Option: k3s**
- See "Advanced: Kubernetes Deployment" section if you want GitOps
- Only recommended if you want to practice k8s or plan multi-machine expansion
- Not necessary for single-server, single-user deployment

### Technology Stack

**Backend:**
- Python 3.11+ (primary language)
- FastAPI for REST API
- Celery with Redis for background jobs
- pandas/NumPy/Polars for data processing
- scikit-learn, XGBoost, PyTorch for ML
- pytest for testing

**Data Storage:**
- PostgreSQL 15+ with TimescaleDB extension (time-series data)
- Redis (caching, rate limiting, Celery broker)
- Optional: MongoDB only if document storage is truly needed

**Frontend:**
- React 18+ with TypeScript (or simple Flask templates for MVP)
- Material-UI or Tailwind CSS
- Lightweight Charts for candlestick/line charts

**Data Sources (Free Tier Priority):**
- **Primary:** yfinance (unlimited, free)
- **Supplementary:** Alpha Vantage (25 req/day free), Financial Modeling Prep
- **News:** NewsAPI free tier, RSS feeds
- **Fundamentals:** SEC EDGAR and SEDAR (free, official sources)

### Key Design Patterns

**Single-User Optimizations:**
- No complex authentication needed (basic auth + VPN access is sufficient)
- No session management across users
- Simple admin interface without role management
- Can run all services on one machine
- Focus on efficient algorithms over horizontal scaling

**Data Flow:**
- Scheduled jobs (Celery Beat) fetch data from APIs
- Raw data validated and stored in TimescaleDB
- Analysis engine calculates indicators and metrics
- Results cached in Redis (critical for API rate limiting)
- Frontend fetches from FastAPI endpoints

**ML Pipeline:**
- Feature engineering from historical data
- Multiple models (ARIMA, Random Forest, LSTM)
- Ensemble predictions with confidence intervals
- Weekly retraining via cron jobs
- Model artifacts stored in Docker volumes
- GPU-accelerated training using nvidia-docker

### Docker Compose Architecture

**Service Organization:**
- **PostgreSQL + TimescaleDB:** Time-series database with persistent volume
- **Redis:** Caching and rate limiting
- **FastAPI Backend:** REST API service
- **Celery Worker:** Background task processing (data fetching, analysis)
- **React Frontend:** Web UI (or simple Flask templates for MVP)
- **Nginx:** Reverse proxy and SSL termination
- **Grafana + Prometheus:** Monitoring (optional in Phase 1)

**Data Persistence:**
- Docker named volumes for all persistent data:
  - `postgres_data`: Database files
  - `redis_data`: Redis persistence (optional)
  - `ml_models`: Model artifacts
  - `backups`: Automated backup storage
- Host bind mounts for configuration files

**Networking:**
- Single Docker bridge network (`stonk-bro-network`)
- Services communicate via service names (Docker DNS)
- Only Nginx exposed to host (ports 80/443)
- Internal services not exposed to host network

**Scheduled Tasks (Host Cron):**
- Replace Celery Beat with simple cron jobs on host
- Trigger via docker exec or API endpoints
- Simpler, more reliable, easier to debug
- Examples:
  ```
  0 17 * * 1-5  docker exec stonk-api python scripts/update_daily_prices.py
  0 2 * * 0     docker exec stonk-api python ml/train_models.py
  0 */6 * * *   docker exec stonk-api python scripts/fetch_news.py
  ```

**Resource Allocation (32GB RAM):**
- PostgreSQL: 8GB (shared_buffers=2GB, effective_cache_size=6GB)
- Redis: 2GB (maxmemory)
- API: 2GB (uvicorn workers)
- Celery Worker: 4GB
- Frontend: 512MB
- ML Training: 12GB (when running, scales down when idle)
- System: 3.5GB buffer

**GPU Access:**
- NVIDIA Docker runtime for ML training containers
- Pass through M2000 GPU to training jobs
- Not needed for inference (CPU sufficient)

## Development Commands

### Initial Server Setup

```bash
# Create environment file
cat > .env << EOF
DB_PASSWORD=your_secure_password
ALPHA_VANTAGE_KEY=your_api_key
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://stockuser:password@postgres:5432/stockdb
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run database migrations
docker-compose exec api alembic upgrade head
```

### Building and Pushing Images

```bash
# Build images locally
docker build -t localhost:5000/stonk-bro/api:latest -f backend/Dockerfile backend/
docker build -t localhost:5000/stonk-bro/frontend:latest -f frontend/Dockerfile frontend/

# Tag for deployment (if using private registry)
docker tag localhost:5000/stonk-bro/api:latest your-registry/stonk-bro/api:v1.0.0
docker tag localhost:5000/stonk-bro/frontend:latest your-registry/stonk-bro/frontend:v1.0.0

# Push to registry
docker push your-registry/stonk-bro/api:v1.0.0
docker push your-registry/stonk-bro/frontend:v1.0.0

# Or import directly to k3s (no registry needed)
docker save localhost:5000/stonk-bro/api:latest | sudo k3s ctr images import -
docker save localhost:5000/stonk-bro/frontend:latest | sudo k3s ctr images import -
```

### Ingress and Certificate Management

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik
EOF

# Ingress will automatically get TLS cert from Let's Encrypt
# See k8s/base/frontend/ingress.yaml for configuration
```

### Monitoring and Troubleshooting

```bash
# Check which containers are running
docker compose ps

# View resource usage (live)
docker stats

# View disk usage by containers
docker system df

# Inspect container details
docker inspect stonk-bro-api-1

# View container IP addresses
docker compose exec api hostname -i

# Check network connectivity between services
docker compose exec api ping postgres
docker compose exec api ping redis

# View Docker logs with JSON output
docker compose logs --json api

# Follow logs for multiple services
docker compose logs -f api celery-worker postgres

# Check PostgreSQL connections
docker compose exec postgres psql -U stockuser -d stockdb -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis memory usage
docker compose exec redis redis-cli INFO memory

# Test API health endpoint
curl http://localhost:8000/health

# Cleanup unused Docker resources
docker system prune -a --volumes  # CAREFUL: removes unused data

# View Docker daemon logs (Ubuntu)
sudo journalctl -u docker -f
```

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run linting
ruff check .
black --check .

# Format code
black .
ruff check --fix .

# Run Celery worker locally
celery -A app.celery worker --loglevel=info

# Run Celery beat (scheduler)
celery -A app.celery beat --loglevel=info

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Frontend Development

```bash
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint
```

### Data Management

```bash
# Fetch initial historical data (one-time setup)
python scripts/fetch_historical_data.py --years 5

# Update daily prices (run via cron or Celery)
python scripts/update_daily_prices.py

# Backfill missing data
python scripts/backfill_data.py --start-date 2020-01-01

# Clean up old data
python scripts/cleanup_old_data.py --days 730
```

### ML Model Training

```bash
# Train all models
python ml/train_models.py --symbols all

# Train specific model
python ml/train_models.py --model lstm --symbols AAPL,GOOGL

# Evaluate model performance
python ml/evaluate_models.py --model-version v1.2

# Generate predictions
python ml/generate_predictions.py --horizon 30
```

## Critical Implementation Details

### TFSA Contribution Room Calculation

The TFSA contribution room calculation is critical and must be accurate:

```python
# Formula: Current Room = Previous Year Room + Annual Limit + Withdrawals - Contributions
# Annual limits by year (update annually):
TFSA_ANNUAL_LIMITS = {
    2009: 5000, 2010: 5000, 2011: 5000, 2012: 5000,
    2013: 5500, 2014: 5500, 2015: 10000, 2016: 5500,
    2017: 5500, 2018: 5500, 2019: 6000, 2020: 6000,
    2021: 6000, 2022: 6000, 2023: 6500, 2024: 7000,
    2025: 7000, 2026: 7000  # Update this annually
}

# User must provide:
# - Birth year (to determine when they turned 18)
# - Historical contributions and withdrawals
# - System calculates available room
```

### API Rate Limiting Strategy

Critical for staying within free tier limits:

```python
# Alpha Vantage: 25 requests/day, 5 requests/minute
# Strategy:
# 1. Cache aggressively (Redis with 1-day TTL for historical data)
# 2. Prioritize portfolio/watchlist stocks
# 3. Use yfinance as primary (unlimited)
# 4. Only use Alpha Vantage for data yfinance doesn't have
# 5. Implement exponential backoff on rate limit errors
# 6. Track API usage in database to monitor limits
```

### Stock Data Schema (TimescaleDB)

```sql
-- Hypertable for price data (optimized for time-series queries)
CREATE TABLE stock_quotes (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    adjusted_close NUMERIC(12, 4),
    PRIMARY KEY (symbol, timestamp)
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('stock_quotes', 'timestamp');

-- Create indexes for common queries
CREATE INDEX idx_stock_quotes_symbol_time ON stock_quotes (symbol, timestamp DESC);
```

### Prediction Model Architecture

**Ensemble Approach:**
1. **ARIMA:** Short-term (1-7 days), fast, good baseline
2. **Random Forest:** Medium-term (1-3 months), handles non-linearity
3. **LSTM:** Long-term (6-12 months), captures temporal patterns
4. **Ensemble:** Weighted average based on historical accuracy per horizon

**Feature Engineering:**
- Price-based: returns, momentum, gaps
- Technical: MA, MACD, RSI, Bollinger Bands
- Fundamental: P/E, ROE, debt ratios (quarterly updates)
- Sentiment: news sentiment scores
- Market context: sector returns, VIX, correlation

**Model Retraining:**
- Daily incremental updates
- Weekly full retraining for short-term models
- Monthly for long-term models
- Trigger immediate retraining if accuracy drops >5%

## Project Structure

When implementing, follow this structure:

```
stonk-bro/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── portfolio.py
│   │   │   │   │   ├── stocks.py
│   │   │   │   │   ├── screening.py
│   │   │   │   │   └── alerts.py
│   │   │   │   └── api.py
│   │   │   └── deps.py
│   │   ├── core/         # Config, security, dependencies
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── db.py
│   │   ├── models/       # SQLAlchemy models
│   │   │   ├── portfolio.py
│   │   │   ├── stock.py
│   │   │   └── alert.py
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   │   ├── data_fetcher.py
│   │   │   ├── analyzer.py
│   │   │   └── screener.py
│   │   └── tasks/        # Celery tasks
│   │       ├── data_tasks.py
│   │       └── ml_tasks.py
│   ├── ml/
│   │   ├── models/       # ML model definitions
│   │   │   ├── arima.py
│   │   │   ├── random_forest.py
│   │   │   └── lstm.py
│   │   ├── features/     # Feature engineering
│   │   │   ├── technical.py
│   │   │   ├── fundamental.py
│   │   │   └── sentiment.py
│   │   ├── training/     # Training scripts
│   │   │   └── train_models.py
│   │   └── inference/    # Prediction generation
│   │       └── predict.py
│   ├── scripts/          # Data fetching, maintenance scripts
│   │   ├── fetch_historical_data.py
│   │   ├── update_daily_prices.py
│   │   ├── fetch_news.py
│   │   └── cleanup_old_data.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/          # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml    # Optional: for poetry
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── Portfolio/
│   │   │   ├── Charts/
│   │   │   ├── Screener/
│   │   │   └── Common/
│   │   ├── pages/        # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Portfolio.tsx
│   │   │   ├── StockDetail.tsx
│   │   │   └── Screener.tsx
│   │   ├── services/     # API clients
│   │   │   └── api.ts
│   │   ├── hooks/        # Custom hooks
│   │   ├── utils/        # Utilities
│   │   └── App.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── nginx/                # Nginx configuration (if using)
│   ├── nginx.conf
│   └── Dockerfile
├── docker/               # Docker-related configs
│   └── postgres/
│       └── init.sql      # Initial DB setup
├── scripts/              # Host-level scripts
│   ├── backup.sh
│   ├── restore.sh
│   └── healthcheck.sh
├── monitoring/           # Optional: Prometheus/Grafana configs
│   ├── prometheus.yml
│   └── grafana-dashboards/
├── docker-compose.yml    # Main deployment file
├── docker-compose.dev.yml  # Development overrides
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Common Pitfalls to Avoid

1. **Over-Engineering:** This is a single-user app. Don't build multi-tenant features, complex auth systems, or horizontal scaling that isn't needed. Keep replica counts at 1 unless you have a specific reason.

2. **API Costs:** Never assume unlimited API access. Always check free tier limits and cache aggressively.

3. **ML Overfitting:** Use proper train/validation/test splits with time-based splitting (no look-ahead bias). Cross-validate.

4. **TFSA Rules:** Don't guess at contribution limits or qualified investments. Use CRA official data.

5. **Security Theater:** Focus on practical security (HTTPS, VPN access, strong passwords) rather than enterprise-grade solutions that add complexity.

6. **Ignoring Data Quality:** Always validate data from external APIs. Price spikes, missing values, and corporate actions need handling.

7. **Real-time Trading:** This is a research and analysis tool, not a high-frequency trading system. End-of-day data is sufficient for most use cases.

8. **Docker/Deployment Pitfalls:**
   - **Not using volumes:** Always use named volumes for persistent data (databases, models)
   - **Missing restart policies:** Set `restart: unless-stopped` or `restart: always` on services
   - **Exposed ports everywhere:** Only expose necessary ports to host (frontend/nginx)
   - **No resource limits:** Set memory/CPU limits in docker-compose.yml to prevent resource exhaustion
   - **Hardcoded values:** Use .env file and environment variables, not hardcoded values
   - **Missing health checks:** Implement healthcheck in docker-compose.yml for reliability
   - **Not backing up volumes:** Schedule regular backups of Docker volumes
   - **Running as root:** Use non-root user in Dockerfiles for security
   - **Missing .dockerignore:** Prevents copying unnecessary files into images

## Performance Optimization

**Database:**
- Use TimescaleDB continuous aggregates for common queries
- Index on (symbol, timestamp DESC) for time-series queries
- Partition old data to cold storage after 2 years

**Caching Strategy:**
- Historical data: 24-hour Redis TTL
- Live quotes: 5-minute TTL during market hours
- Fundamental data: 1-week TTL
- Predictions: Until next model run

**Background Jobs:**
- Data fetching: Run after market close (4:30 PM ET)
- Model training: Run overnight (low resource usage hours)
- News aggregation: Every 6 hours
- Alert checks: Every 5-15 minutes

## Testing Strategy

**Unit Tests:**
- All service functions
- Feature engineering logic
- TFSA calculation accuracy
- API rate limiting

**Integration Tests:**
- API endpoints with test database
- Celery task execution
- Database migrations
- External API mocking

**ML Model Tests:**
- Prediction accuracy within thresholds
- Feature importance sanity checks
- Model serialization/deserialization
- Confidence interval coverage

## Monitoring and Maintenance

**Health Checks:**
- API availability
- Database connectivity
- Redis connectivity
- Celery worker status
- Disk space (time-series data grows)

**Key Metrics to Track:**
- API rate limit usage (stay under limits)
- Model prediction accuracy (MAPE)
- Database query performance
- Cache hit rates
- Background job success/failure rates

**Backup Strategy:**
- Daily PostgreSQL dumps to external drive
- Weekly full system backup
- Test restore procedure quarterly
- Optional: Backblaze B2 for offsite backup ($0-5/month)

## Implementation Roadmap

**Phase 1 - MVP (Months 1-3):**
- Portfolio tracking (manual entry)
- Basic screener (fundamental filters)
- Price charts with technical indicators
- Email alerts
- TFSA contribution tracking
- Docker Compose deployment with systemd integration
- Basic monitoring (docker stats, logs)

**Phase 2 - Analytics (Months 4-6):**
- Advanced technical analysis
- News aggregation and sentiment
- Watchlists
- Performance analytics
- Benchmark comparison

**Phase 3 - ML Predictions (Months 7-9):**
- Price prediction models (ARIMA, Random Forest, LSTM)
- Confidence intervals
- Model accuracy tracking
- Backtesting framework

**Phase 4 - Polish (Months 10-12):**
- Mobile-responsive PWA
- Advanced charting
- Export/reporting
- Optional: Broker integration (Questrade API)

## Docker Compose Configuration Example

### Complete docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: stonk-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"  # Expose for pgAdmin/debugging (remove in production)
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '2.0'
        reservations:
          memory: 4G

  redis:
    image: redis:7-alpine
    container_name: stonk-redis
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"  # Expose for debugging (remove in production)
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '0.5'

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: stonk-api
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      ALPHA_VANTAGE_KEY: ${ALPHA_VANTAGE_KEY}
      NEWS_API_KEY: ${NEWS_API_KEY}
      ENVIRONMENT: ${ENVIRONMENT}
      LOG_LEVEL: ${LOG_LEVEL}
    volumes:
      - ./backend:/app  # For development (remove for production)
      - ml_models:/app/ml/artifacts
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: stonk-celery-worker
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      ALPHA_VANTAGE_KEY: ${ALPHA_VANTAGE_KEY}
      NEWS_API_KEY: ${NEWS_API_KEY}
      ENVIRONMENT: ${ENVIRONMENT}
    volumes:
      - ./backend:/app
      - ml_models:/app/ml/artifacts
    depends_on:
      - redis
      - postgres
      - api
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    command: celery -A app.celery worker --loglevel=info --concurrency=2

  # ML Training service (runs on-demand with GPU)
  ml-trainer:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: stonk-ml-trainer
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
    volumes:
      - ./backend:/app
      - ml_models:/app/ml/artifacts
    depends_on:
      - postgres
      - redis
    restart: "no"  # Manual start only
    deploy:
      resources:
        limits:
          memory: 12G
          cpus: '4.0'
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    profiles:
      - ml-training  # Only start with: docker compose --profile ml-training up

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: stonk-frontend
    environment:
      REACT_APP_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - api
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    container_name: stonk-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # If using SSL
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - api
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'

  # Optional: Grafana for monitoring
  grafana:
    image: grafana/grafana:latest
    container_name: stonk-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-clock-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    restart: unless-stopped
    profiles:
      - monitoring
    deploy:
      resources:
        limits:
          memory: 512M

  # Optional: Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: stonk-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped
    profiles:
      - monitoring
    deploy:
      resources:
        limits:
          memory: 1G

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  ml_models:
    driver: local
  grafana_data:
    driver: local
  prometheus_data:
    driver: local

networks:
  default:
    name: stonk-bro-network
```

### Example .env File

```bash
# Database Configuration
POSTGRES_USER=stockuser
POSTGRES_DB=stockdb
DB_PASSWORD=your_very_secure_password_here

# Database URL for application
DATABASE_URL=postgresql://stockuser:${DB_PASSWORD}@postgres:5432/stockdb

# Redis
REDIS_URL=redis://redis:6379

# API Keys (get from providers)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key

# Application Config
ENVIRONMENT=production
LOG_LEVEL=info

# Monitoring (optional)
GRAFANA_PASSWORD=your_grafana_password
```

### Backend Dockerfile Example

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 stonkuser && chown -R stonkuser:stonkuser /app
USER stonkuser

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## External Resources

- **Spec Document:** See `stock-research-app-spec.md` for complete requirements
- **yfinance Docs:** https://github.com/ranaroussi/yfinance
- **Alpha Vantage API:** https://www.alphavantage.co/documentation/
- **TimescaleDB Docs:** https://docs.timescale.com/
- **TFSA Rules:** https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account.html
- **Docker Compose Docs:** https://docs.docker.com/compose/
- **NVIDIA Docker:** https://github.com/NVIDIA/nvidia-docker
- **FastAPI Docs:** https://fastapi.tiangolo.com/

## Notes for Claude Code

- When implementing features, prioritize simplicity and maintainability over premature optimization
- Always consider API rate limits when adding data fetching code
- TFSA contribution calculations must be precise - validate against CRA documentation
- ML predictions should include confidence intervals and uncertainty communication
- Single-user, single-server deployment = Docker Compose is the right tool
- Use Docker volumes for all persistent data (never store data in containers)
- Leverage host cron jobs for scheduled tasks (simpler than Celery Beat)
- Set resource limits in docker-compose.yml to prevent any service from consuming all 32GB RAM
- Use GPU passthrough (`--gpus all`) only for ML training, not inference
- Test ML models thoroughly before trusting predictions
- Cache aggressively to minimize API usage and costs
- Always use environment variables (.env file) for configuration, never hardcode

## Advanced: Kubernetes Deployment (Optional)

If you later want to migrate to Kubernetes or deploy across multiple machines, k3s is recommended. The architecture principles remain the same:

**When to consider k3s:**
- You add more physical servers to the homelab
- You want to practice Kubernetes/GitOps workflows
- You need better resource isolation between workloads
- You want automated rollbacks and canary deployments

**Migration path:**
1. Docker Compose images work directly in k8s
2. Convert docker-compose.yml to k8s manifests (kompose tool)
3. Use Kustomize for environment-specific configs
4. Deploy with `kubectl apply -k k8s/overlays/production`

The Docker Compose setup provides a solid foundation and can be containerized into k8s manifests when/if needed.
