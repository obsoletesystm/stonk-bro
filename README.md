# Stonk Bro - Personal Stock Research Platform

A self-hosted stock research and prediction platform for managing a Canadian TFSA portfolio. Built with FastAPI, PostgreSQL + TimescaleDB, and Machine Learning.

## Features

- 📊 **Portfolio Tracking** - Track holdings, transactions, and performance
- 🔍 **Stock Screening** - Filter stocks by fundamental and technical criteria
- 📈 **Price Alerts** - Get notified when prices hit targets
- 🤖 **ML Predictions** - ARIMA, Random Forest, and LSTM price predictions
- 💰 **TFSA Tracking** - Calculate contribution room and manage tax-free accounts
- 📰 **News & Sentiment** - Aggregate news with sentiment analysis
- 📉 **Technical Analysis** - Calculate indicators and identify patterns

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- NVIDIA Docker runtime (optional, for GPU ML training)
- 32GB RAM recommended
- 100GB+ free disk space

### Initial Setup

1. **Clone the repository** (or you're already in it)

```bash
cd ~/Documents/code/stonk-bro
```

2. **Create environment file**

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

**Required settings:**
- `DB_PASSWORD` - Set a secure database password
- `ALPHA_VANTAGE_KEY` - Get free key from https://www.alphavantage.co/support/#api-key
- `NEWS_API_KEY` - Get free key from https://newsapi.org/register

3. **Start the services**

```bash
# Start core services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

4. **Run database migrations**

```bash
# Create initial migration
docker compose exec api alembic revision --autogenerate -m "Initial schema"

# Apply migrations
docker compose exec api alembic upgrade head
```

5. **Access the application**

- **Frontend:** http://server.local:3000 or http://localhost:3000
- **API Docs:** http://server.local:8000/docs
- **API ReDoc:** http://server.local:8000/redoc
- **Health Check:** http://server.local:8000/health

### Test the API

```bash
# Get a stock quote
curl http://localhost:8000/api/v1/stocks/quote/AAPL

# Get historical data
curl "http://localhost:8000/api/v1/stocks/history/AAPL?period=1mo"

# Search for stocks
curl http://localhost:8000/api/v1/stocks/search/apple

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed
```

## Production Deployment

### 1. Set up systemd auto-start

```bash
# Copy systemd service file
sudo cp systemd/stonk-bro.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/stonk-bro.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable stonk-bro
sudo systemctl start stonk-bro

# Check status
sudo systemctl status stonk-bro
```

### 2. Set up scheduled tasks (cron)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths as needed):

# Daily data fetch (5 PM ET, weekdays)
0 17 * * 1-5 cd /home/willmcnaughton/Documents/code/stonk-bro && docker compose exec -T api python scripts/update_daily_prices.py >> /var/log/stonk-bro-fetch.log 2>&1

# Weekly model training (Sunday 2 AM)
0 2 * * 0 cd /home/willmcnaughton/Documents/code/stonk-bro && docker compose --profile ml-training run --rm ml-trainer >> /var/log/stonk-bro-training.log 2>&1

# Daily backup (3 AM)
0 3 * * * /home/willmcnaughton/Documents/code/stonk-bro/scripts/backup.sh /backups/stonk-bro >> /var/log/stonk-bro-backup.log 2>&1

# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/stonk-bro-{fetch,training,backup}.log
sudo chown $USER:$USER /var/log/stonk-bro-*.log
```

### 3. Optional: Set up monitoring

```bash
# Start with monitoring stack
docker compose --profile monitoring up -d

# Access Grafana
# URL: http://server.local:3001
# Default credentials: admin / admin (change on first login)

# Access Prometheus
# URL: http://server.local:9090
```

## Common Operations

### Managing Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a specific service
docker compose restart api

# View logs
docker compose logs -f api

# Execute commands in containers
docker compose exec api bash
docker compose exec postgres psql -U stockuser stockdb
docker compose exec redis redis-cli

# Check resource usage
docker stats
```

### Database Operations

```bash
# Create new migration
docker compose exec api alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker compose exec api alembic upgrade head

# Rollback migration
docker compose exec api alembic downgrade -1

# Access database
docker compose exec postgres psql -U stockuser stockdb

# Backup database
./scripts/backup.sh /backups/stonk-bro

# Restore database
./scripts/restore.sh /backups/stonk-bro/stonk-bro-backup-20260106.sql.gz
```

### ML Training

```bash
# Train models with GPU
docker compose --profile ml-training run --rm ml-trainer

# Train specific model
docker compose exec api python ml/training/train_models.py --model arima

# View model artifacts
ls -lh backend/ml/artifacts/
```

### Health Checks

```bash
# Run health check script
./scripts/healthcheck.sh

# Manual checks
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/detailed
docker compose ps
```

## Development

### Local Development

```bash
# Install Python dependencies locally (optional)
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Lint code
ruff check .
black --check .

# Format code
black .
```

### Adding New Endpoints

1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add router to `backend/app/api/v1/api.py`
3. Test with: `http://localhost:8000/docs`

### Adding Database Models

1. Create model in `backend/app/models/`
2. Import in `backend/app/models/__init__.py`
3. Create migration: `docker compose exec api alembic revision --autogenerate -m "description"`
4. Apply: `docker compose exec api alembic upgrade head`

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs api

# Check if ports are in use
sudo lsof -i :8000
sudo lsof -i :5432

# Rebuild containers
docker compose down
docker compose up -d --build
```

### Database connection errors

```bash
# Check if PostgreSQL is healthy
docker compose exec postgres pg_isready -U stockuser

# Check database logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### API errors

```bash
# Check API logs
docker compose logs -f api

# Execute shell in container
docker compose exec api bash

# Test database connection
docker compose exec api python -c "from app.core.db import engine; engine.connect()"
```

### GPU not working

```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# If fails, install nvidia-docker2
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Project Structure

```
stonk-bro/
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── tasks/       # Celery tasks
│   ├── ml/              # Machine learning
│   ├── scripts/         # Data fetching scripts
│   ├── tests/           # Tests
│   └── alembic/         # Database migrations
├── frontend/            # Web interface
├── nginx/               # Nginx configuration
├── scripts/             # Utility scripts
├── systemd/             # Systemd service files
├── docker-compose.yml   # Docker Compose configuration
└── .env                 # Environment variables (create from .env.example)
```

## Resources

- **Documentation:** See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guide
- **Spec:** See [stock-research-app-spec.md](stock-research-app-spec.md) for complete feature specifications
- **API Docs:** http://localhost:8000/docs (when running)

## License

Personal use only.

## Support

This is a personal project. See [CLAUDE.md](CLAUDE.md) for implementation notes and architecture decisions.
