# Automated Stock Research and Prediction Application
## Specification Document
### For Canadian TFSA Investment Portfolio Management

**Version:** 1.0  
**Date:** January 6, 2026  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Purpose and Goals](#purpose-and-goals)
3. [Target User Profile](#target-user-profile)
4. [Functional Requirements](#functional-requirements)
5. [Technical Architecture](#technical-architecture)
6. [Data Sources and Integration](#data-sources-and-integration)
7. [Machine Learning Models](#machine-learning-models)
8. [User Interface Design](#user-interface-design)
9. [Security and Compliance](#security-and-compliance)
10. [TFSA-Specific Features](#tfsa-specific-features)
11. [Performance Metrics](#performance-metrics)
12. [Implementation Roadmap](#implementation-roadmap)
13. [Risk Management](#risk-management)
14. [Appendices](#appendices)

---

## 1. Executive Summary

This document outlines the technical and functional specifications for a personal automated stock research and prediction platform designed for managing a Tax-Free Savings Account (TFSA) portfolio in Canada. The application combines real-time market data analysis, fundamental research, technical indicators, and machine learning-based prediction models to support informed investment decisions within the TFSA framework.

The system is designed as a personal decision support tool that aggregates multiple data sources, performs automated analysis, and presents actionable insights while remaining compliant with Canadian securities regulations and TFSA rules. It emphasizes risk management, portfolio diversification, and long-term wealth accumulation within tax-advantaged accounts.

**Personal Infrastructure:** This is a single-user platform self-hosted on a dedicated bare-metal server in a home environment, eliminating recurring cloud costs entirely. The architecture leverages Docker Compose, open-source tools, and free-tier data sources to minimize expenses. A single dedicated server (Intel Xeon E3-1240 v5, 32GB RAM, 500GB storage, NVIDIA M2000 GPU) runs all services with annual operating expenses limited to electricity ($100-$300) and optional domain registration ($10-15).

### Key Features

- Automated stock screening based on fundamental and technical criteria
- Multi-model price prediction with confidence intervals
- Real-time portfolio tracking and performance analytics
- TFSA contribution room monitoring and optimization
- News sentiment analysis and event detection
- Customizable alerts and notifications
- Risk assessment and position sizing recommendations

---

## 2. Purpose and Goals

### 2.1 Primary Objectives

The application aims to streamline the investment research process by automating data collection, analysis, and presentation of investment opportunities suitable for TFSA accounts. It reduces the time required for manual research while improving decision quality through systematic analysis and data-driven insights. The system provides continuous monitoring of portfolio holdings and market conditions, alerting users to significant developments that may warrant action.

### 2.2 Key Goals

- Identify high-quality investment opportunities across Canadian and U.S. exchanges
- Generate short-term and long-term price predictions using multiple analytical models
- Monitor portfolio performance and risk metrics in real-time
- Optimize TFSA contribution strategies and track contribution room
- Maintain compliance with Canadian regulations for qualified TFSA investments
- Provide educational context to improve user investment knowledge
- Enable backtesting of strategies using historical data

### 2.3 Success Metrics

- User portfolio returns compared to benchmark indices (S&P/TSX Composite, S&P 500)
- Prediction accuracy measured by mean absolute percentage error (MAPE)
- User engagement metrics including daily active users and session duration
- Alert relevance and user action rate
- System uptime and data accuracy
- User satisfaction scores from periodic surveys

---

## 3. Target User Profile

### 3.1 User Profile (You)

**Profile:** Canadian investor actively managing personal TFSA portfolio

**Characteristics:**
- Investment knowledge: Intermediate to advanced level
- Portfolio size: Variable TFSA holdings
- Holdings: 10-30+ positions across various sectors
- Trading frequency: Weekly to monthly reviews
- Time availability: Variable, platform provides efficiency
- Technology comfort: High, comfortable with self-hosting and technical platforms
- Home lab capable: Ability to run and maintain Kubernetes cluster

**Goals:**
- Maximize long-term returns within TFSA tax advantages
- Build diversified portfolio across sectors and geographies
- Identify growth opportunities early through systematic analysis
- Avoid significant losses through risk management and alerts
- Stay informed about portfolio holdings without constant manual monitoring
- Make data-driven investment decisions backed by multiple analytical models
- Leverage automation to reduce research time while improving quality

**Pain Points Addressed:**
- Limited time for comprehensive research across multiple stocks
- Information overload from disparate sources
- Difficulty tracking multiple positions and metrics simultaneously
- Uncertainty about optimal timing for buy/sell decisions
- Need for systematic approach to avoid emotional decision-making
- Desire for ML-based predictions without relying on external services

**Technical Capabilities:**
- Can set up and maintain Kubernetes infrastructure
- Comfortable with command-line tools and configuration
- Ability to troubleshoot technical issues
- Understanding of Docker, containers, and orchestration
- Self-sufficient for system administration

---

## 4. Functional Requirements

### 4.1 Stock Screening and Discovery

**Purpose:** Help users discover investment opportunities that match their criteria.

**Features:**

**Fundamental Filters:**
- Price-to-Earnings (P/E) ratio ranges
- Earnings growth rates (quarterly and annual)
- Revenue growth rates
- Dividend yield thresholds
- Profit margins (gross, operating, net)
- Return on Equity (ROE) and Return on Assets (ROA)
- Debt-to-Equity ratio limits
- Free cash flow metrics
- Piotroski F-Score for financial strength

**Technical Filters:**
- Price momentum (1-month, 3-month, 6-month returns)
- Moving average positions (above/below 50-day, 200-day MA)
- RSI levels (oversold/overbought conditions)
- Volume patterns (above average volume)
- 52-week high/low proximity
- Price breakouts from consolidation
- Volatility metrics (beta, standard deviation)

**Market Filters:**
- Market capitalization ranges (micro, small, mid, large cap)
- Sector and industry classification
- Exchange listing (TSX, TSXV, NYSE, NASDAQ)
- Geographic region (Canada, U.S., international)
- TFSA eligibility status

**Screening Execution:**
- On-demand screening with immediate results
- Scheduled screening (daily, weekly) with email reports
- Saved screen templates for quick reuse
- Relevance scoring based on criteria match
- Results exportable to CSV or PDF
- Historical screening results archive

**Output:**
- Ranked list of matching stocks
- Key metrics summary for each result
- Quick-view charts and trends
- One-click add to watchlist or portfolio
- Comparison matrix for multiple stocks

### 4.2 Fundamental Analysis

**Purpose:** Provide comprehensive financial analysis of individual companies.

**Data Collection:**
- Automated retrieval of quarterly and annual financial statements
- Income statements (5+ years historical)
- Balance sheets (5+ years historical)
- Cash flow statements (5+ years historical)
- Management discussion and analysis (MD&A)
- Insider transaction records
- Institutional ownership data

**Calculated Metrics:**

**Profitability:**
- Gross profit margin trends
- Operating profit margin trends
- Net profit margin trends
- Return on Equity (ROE)
- Return on Assets (ROA)
- Return on Invested Capital (ROIC)

**Liquidity:**
- Current ratio
- Quick ratio
- Cash ratio
- Operating cash flow ratio

**Leverage:**
- Debt-to-Equity ratio
- Debt-to-Assets ratio
- Interest coverage ratio
- Debt service coverage ratio

**Efficiency:**
- Asset turnover ratio
- Inventory turnover ratio
- Receivables turnover ratio
- Days sales outstanding

**Valuation:**
- Price-to-Earnings (P/E) ratio
- Price-to-Book (P/B) ratio
- Price-to-Sales (P/S) ratio
- Enterprise Value to EBITDA (EV/EBITDA)
- PEG ratio (P/E to Growth)
- Dividend yield and payout ratio

**Analysis Features:**
- Trend identification over multiple periods
- Peer comparison against 5-10 similar companies
- Industry average comparisons
- Historical percentile rankings
- Quality score based on financial health
- Red flag detection (deteriorating metrics)
- Earnings quality analysis
- Management effectiveness indicators

**Visualization:**
- Financial statement line charts
- Metric comparison bar charts
- Peer comparison tables
- Trend arrows and color coding
- Interactive financial calculator

### 4.3 Technical Analysis

**Purpose:** Identify trading opportunities and optimal entry/exit points through price and volume patterns.

**Technical Indicators:**

**Trend Indicators:**
- Simple Moving Averages (10, 20, 50, 100, 200-day)
- Exponential Moving Averages (12, 26, 50-day)
- Moving Average Convergence Divergence (MACD)
- Average Directional Index (ADX)
- Parabolic SAR

**Momentum Indicators:**
- Relative Strength Index (RSI)
- Stochastic Oscillator
- Commodity Channel Index (CCI)
- Rate of Change (ROC)
- Williams %R

**Volatility Indicators:**
- Bollinger Bands
- Average True Range (ATR)
- Keltner Channels
- Standard deviation

**Volume Indicators:**
- On-Balance Volume (OBV)
- Volume-Weighted Average Price (VWAP)
- Accumulation/Distribution Line
- Chaikin Money Flow

**Pattern Recognition:**

**Chart Patterns:**
- Head and Shoulders (bullish/bearish)
- Double Tops and Double Bottoms
- Triple Tops and Triple Bottoms
- Ascending and Descending Triangles
- Symmetrical Triangles
- Flags and Pennants
- Wedges (rising/falling)
- Cup and Handle
- Rounding Bottom

**Candlestick Patterns:**
- Doji, Hammer, Shooting Star
- Engulfing patterns
- Morning Star, Evening Star
- Three White Soldiers, Three Black Crows
- Harami patterns

**Support and Resistance:**
- Automatic identification of key price levels
- Pivot points calculation
- Fibonacci retracement levels
- Fibonacci extension levels
- Psychological price levels (round numbers)

**Features:**
- Interactive charting with multiple timeframes (1-minute to monthly)
- Drawing tools for trendlines, channels, and annotations
- Multi-indicator overlay capability
- Comparison charts (relative strength vs. indices)
- Signal generation based on indicator crossovers
- Backtest indicator strategies against historical data
- Alert creation for technical conditions

### 4.4 Price Prediction Models

**Purpose:** Generate probabilistic price forecasts for multiple time horizons to support investment timing decisions.

**Prediction Timeframes:**
- 1 week ahead
- 1 month ahead
- 3 months ahead
- 6 months ahead
- 1 year ahead

**Model Types:**

**Statistical Models:**
- ARIMA (AutoRegressive Integrated Moving Average)
- GARCH (Generalized AutoRegressive Conditional Heteroskedasticity) for volatility
- Linear regression with technical features
- Exponential smoothing methods

**Machine Learning Models:**
- Random Forest Regressors
- Gradient Boosting Machines (XGBoost, LightGBM)
- Support Vector Machines (SVM)
- K-Nearest Neighbors (KNN)

**Deep Learning Models:**
- Long Short-Term Memory (LSTM) networks
- Gated Recurrent Units (GRU)
- Convolutional Neural Networks (CNN) for pattern recognition
- Transformer models for sequence prediction

**Ensemble Methods:**
- Weighted average of multiple models
- Stacking ensemble with meta-learner
- Dynamic weighting based on recent accuracy
- Confidence-weighted predictions

**Input Features:**
- Historical price and volume data
- Technical indicators (50+ features)
- Fundamental metrics (quarterly updates)
- Sentiment scores from news and social media
- Market regime indicators (volatility, trend strength)
- Sector and market index movements
- Macroeconomic indicators (interest rates, inflation)

**Model Output:**
- Point prediction (expected price)
- Confidence intervals (80%, 90%, 95%)
- Probability distributions
- Upside/downside scenarios
- Expected return percentage
- Risk-adjusted return forecast

**Model Management:**
- Automated retraining on rolling window basis
- Cross-validation for hyperparameter tuning
- Out-of-sample testing for performance evaluation
- Model versioning and A/B testing
- Feature importance analysis
- Prediction explanation using SHAP values

**Accuracy Tracking:**
- Mean Absolute Error (MAE)
- Mean Absolute Percentage Error (MAPE)
- Root Mean Squared Error (RMSE)
- Direction accuracy (up/down prediction)
- Sharpe ratio of predicted returns
- Historical prediction vs. actual charts
- Per-model and per-stock accuracy metrics

**User Interface:**
- Prediction chart with confidence bands
- Multiple scenario visualization
- Model comparison view
- Historical accuracy display
- Forecast update frequency indicator
- Explanation of key driving factors

### 4.5 Portfolio Management

**Purpose:** Track, analyze, and optimize TFSA investment portfolio performance.

**Portfolio Setup:**
- Manual entry of holdings with purchase details
- Import from broker statements (CSV upload)
- Real-time synchronization with broker APIs (future feature)
- Multiple portfolio support (TFSA, RRSP, non-registered)
- Cash position tracking
- Transaction history with cost basis

**Real-Time Tracking:**
- Current market value calculation
- Unrealized gains/losses by position
- Realized gains/losses from closed positions
- Intraday changes and alerts
- Automatic quote refresh (configurable intervals)
- After-hours price tracking

**Performance Analytics:**

**Returns:**
- Total return (percentage and dollar value)
- Annualized return (CAGR)
- Time-weighted return (TWR)
- Money-weighted return (IRR)
- Returns by period (daily, weekly, monthly, yearly)
- Returns by holding period for each position

**Risk Metrics:**
- Portfolio beta relative to benchmarks
- Standard deviation of returns
- Sharpe ratio (risk-adjusted return)
- Sortino ratio (downside risk-adjusted)
- Maximum drawdown
- Value at Risk (VaR) at 95% confidence
- Correlation matrix between holdings

**Allocation Analysis:**
- Sector allocation pie chart
- Industry breakdown
- Geographic exposure
- Market cap distribution
- Asset class allocation
- Currency exposure (CAD vs. USD)
- Top 10 holdings concentration

**Dividend Tracking:**
- Upcoming dividend payments calendar
- Dividend yield by position
- Total portfolio yield
- Dividend growth tracking
- Reinvestment tracking (DRIP)
- Annual dividend income projection

**Rebalancing:**
- Target allocation setting by sector/asset
- Deviation alerts from target allocations
- Rebalancing suggestions with trade recommendations
- Tax-efficient rebalancing (TFSA context)
- Cost-benefit analysis of rebalancing

**Comparison and Benchmarking:**
- S&P/TSX Composite Index comparison
- S&P 500 Index comparison (CAD adjusted)
- Sector-specific benchmark comparison
- Custom benchmark creation
- Relative performance charts
- Alpha and tracking error calculation

**Position Sizing:**
- Risk-based position sizing calculator
- Kelly Criterion calculator
- Equal-weight vs. cap-weight strategies
- Concentration risk warnings
- Suggested position sizes for new purchases

**Tax Reporting:**
- TFSA contribution tracking
- TFSA withdrawal tracking
- US withholding tax on dividends (information only)
- Annual summary reports
- Transaction export for tax software

### 4.6 News and Sentiment Analysis

**Purpose:** Aggregate and analyze market-moving news to inform investment decisions.

**News Sources:**
- Financial news websites (Bloomberg, Reuters, Financial Post, Globe and Mail)
- Company press releases and investor relations
- SEC filings (8-K, 10-K, 10-Q) and SEDAR filings
- Analyst reports and rating changes
- Social media (Twitter/X, StockTwits, Reddit)
- Earnings call transcripts
- Industry publications

**News Aggregation:**
- Real-time news feed for portfolio holdings
- Sector and market-level news
- Customizable news filters by source and topic
- Deduplication of similar stories
- Relevance ranking
- Translation of non-English sources

**Sentiment Analysis:**
- Natural Language Processing (NLP) models
- Sentiment classification (positive, negative, neutral)
- Sentiment intensity scoring (-1.0 to +1.0)
- Entity recognition (companies, people, products)
- Topic extraction and categorization
- Sentiment trends over time

**Event Detection:**
- Earnings announcements and surprises
- Dividend announcements and changes
- Mergers and acquisitions
- Management changes (CEO, CFO transitions)
- Product launches and approvals
- Regulatory actions and legal issues
- Stock splits and special dividends
- Share buyback programs
- Analyst upgrades/downgrades
- Unusual trading activity

**Sentiment Indicators:**
- Per-stock sentiment score
- Sector sentiment aggregation
- Market-wide sentiment gauge
- Social media buzz metrics
- News volume and velocity
- Sentiment momentum and reversals
- Fear and Greed index

**Integration with Analysis:**
- Sentiment as input feature for predictions
- Event-based alert generation
- News-driven screening filters
- Correlation between sentiment and price movements
- Pre-earnings sentiment analysis

**User Features:**
- Customizable news dashboard
- Keyword-based news alerts
- Saved news searches
- Article tagging and notes
- News impact on portfolio holdings
- Historical news archive with search

### 4.7 Alerts and Notifications

**Purpose:** Keep users informed of important market developments and portfolio changes without constant monitoring.

**Alert Types:**

**Price Alerts:**
- Price crosses above/below specific level
- Percentage move (up/down) over period
- New 52-week high or low
- Gap up/gap down at market open
- Approaching support or resistance level

**Technical Alerts:**
- Moving average crossovers (golden cross, death cross)
- RSI overbought/oversold levels
- MACD signal line crossovers
- Bollinger Band breaks
- Volume spike (above average)
- Breakout from chart pattern
- Trend reversal signals

**Fundamental Alerts:**
- Earnings announcement date approaching
- Earnings report released (beat/miss)
- Dividend announcement
- Ex-dividend date approaching
- Analyst rating change
- Insider transaction (buy/sell)
- SEC/SEDAR filing

**Portfolio Alerts:**
- Position gain/loss exceeds threshold
- Total portfolio value milestone
- Rebalancing needed (allocation drift)
- Sector overconcentration
- High correlation risk detected
- Drawdown exceeds limit

**News Alerts:**
- Breaking news for portfolio holdings
- Negative sentiment spike
- Major sector or market event
- Regulatory news affecting holdings

**Prediction Alerts:**
- New price prediction available
- Prediction confidence change
- Significant forecast revision
- Target price reached

**TFSA Alerts:**
- Contribution room available (January 1)
- Approaching contribution limit
- Withdrawal processed (affects future room)
- Over-contribution warning

**Alert Configuration:**
- User-defined thresholds and conditions
- Multiple alert types per stock
- Watchlist and portfolio alert separation
- Alert frequency limits (avoid spam)
- Quiet hours configuration
- Alert priority levels

**Delivery Channels:**
- Email notifications
- Push notifications (mobile app)
- SMS text messages (premium feature)
- In-app notification center
- Webhook integrations for advanced users

**Alert Management:**
- Alert history and audit log
- Mark as read/unread
- Snooze temporarily
- Bulk enable/disable
- Alert templates for quick setup
- Smart filtering to reduce noise

### 4.8 Watchlist Management

**Purpose:** Monitor potential investment opportunities before committing capital.

**Features:**
- Unlimited watchlists with custom names
- Add stocks from screener or search
- Quick view of key metrics for all watchlist items
- Real-time price updates
- Mini-charts for each watchlist item
- Sorting and filtering within watchlist
- Notes and tags per stock
- Performance tracking (as if invested)
- Share watchlists with other users (future)
- Export watchlist to CSV

**Watchlist Analytics:**
- Average P/E, dividend yield of list
- Sector composition
- Momentum leaders and laggards
- Top gainers/losers
- Stocks near buy points
- Stocks meeting user criteria

---

## 5. Technical Architecture

### 5.1 Architecture Decision (Single Dedicated Server)

**Deployment Strategy:**

**Primary: Docker Compose**
- Single dedicated server = Docker Compose is the right tool
- All services orchestrated via docker-compose.yml
- Managed by systemd for auto-start on boot
- Host cron jobs for scheduled tasks (simpler than Celery Beat)
- Direct access to all 32GB RAM and GPU resources
- Simple debugging with docker logs and docker stats
- Minimal orchestration overhead (~1-2% vs k8s ~5-10%)
- Fast deployment and iteration

**Why Not Kubernetes?**
- Single machine doesn't benefit from orchestration
- Unnecessary complexity for personal use
- Harder to debug and maintain
- No high availability needed (single user)
- Docker Compose provides all needed features

**Advanced Option: k3s**
- Only if adding more physical servers later
- Or if wanting to practice GitOps workflows
- Migration path exists via kompose tool
- Not recommended for initial implementation

**Hardware Configuration:**
- Intel Xeon E3-1240 v5 (4 cores, 8 threads @ 3.5GHz)
- 32GB RAM
- 500GB storage
- NVIDIA Quadro M2000 (4GB VRAM, CUDA-capable)
- Ubuntu 24.04 LTS
- Hostname: server.local

**Database Choice:**
- PostgreSQL 15+ with TimescaleDB extension (time-series optimization)
- Redis 7 for caching and rate limiting
- Both run as Docker containers with persistent volumes
- MongoDB not needed - PostgreSQL handles all data types

**Frontend Choice:**
- React 18+ with TypeScript for rich interactive experience
- Or simple FastAPI templates with Jinja2 for MVP (faster to implement)
- Responsive design for mobile browser access
- No native mobile app needed - PWA sufficient

### 5.2 System Overview

The application follows a Docker Compose architecture optimized for single-user deployment on a dedicated server. All services run as containers orchestrated by Docker Compose, with systemd managing the compose stack for auto-start and reliability.

**Architecture Layers:**

1. **Presentation Layer:** React web UI or FastAPI templates
2. **Reverse Proxy:** Nginx for SSL termination and routing
3. **API Layer:** FastAPI backend serving REST endpoints
4. **Application Layer:** Celery workers for background tasks
5. **Data Layer:** PostgreSQL + TimescaleDB, Redis
6. **ML Layer:** Training services with GPU access (on-demand)
7. **Integration Layer:** External API connections (yfinance, Alpha Vantage)

**Docker Compose Services:**
- **nginx:** Reverse proxy, SSL termination (ports 80/443)
- **frontend:** React app or FastAPI templates (port 3000)
- **api:** FastAPI backend (port 8000)
- **celery-worker:** Background task processing
- **postgres:** TimescaleDB for time-series data
- **redis:** Caching and message broker
- **ml-trainer:** GPU-enabled training (on-demand via profile)
- **grafana:** Monitoring dashboard (optional)
- **prometheus:** Metrics collection (optional)

**Simplified Single-User Design:**
- No authentication needed (VPN or LAN access only)
- No session management or user accounts
- Single database instance, no replication
- No horizontal scaling or load balancing
- All services on one server
- Direct GPU access for ML training

### 5.3 Core Components

**Data Ingestion Service:**
- Host cron jobs trigger data fetching scripts via `docker exec`
- Runs after market close (5 PM ET weekdays)
- Python scripts fetch from yfinance (primary), Alpha Vantage (supplementary)
- Data validation and storage in TimescaleDB
- Rate limit tracking in Redis
- Simpler than Celery Beat, easier to debug

**Analysis Engine:**
- Celery workers calculate technical indicators
- Compute fundamental metrics from stored data
- Pattern recognition using TA-Lib
- Results cached in Redis
- Runs as background tasks or on-demand via API

**Prediction Service:**
- ML model training via GPU-enabled container
- Triggered by cron job (weekly) or manually
- Uses NVIDIA M2000 for LSTM/neural network training
- scikit-learn, XGBoost, PyTorch stack
- Model artifacts stored in Docker volume (`ml_models`)
- Predictions generated in batch, cached in database

**Portfolio Service:**
- FastAPI endpoints for portfolio CRUD operations
- Real-time valuation using cached price data
- Performance metrics calculated on-demand
- Transaction history in PostgreSQL
- SQLAlchemy ORM for database access

**Alert Service:**
- Celery periodic tasks check alert conditions
- Email notifications via SMTP
- Simple rule engine evaluates thresholds
- Runs every 5-15 minutes during market hours
- Alert history stored in database

**News Service:**
- RSS feed aggregation + NewsAPI (free tier)
- Scheduled updates via cron (4x daily)
- Sentiment analysis using FinBERT or similar
- Stored in PostgreSQL (no separate document store needed)

**Web Interface:**
- FastAPI serves REST API endpoints
- React SPA frontend (or Jinja2 templates for MVP)
- Nginx reverse proxy handles routing
- Responsive design for desktop and mobile browsers
- No WebSockets needed - polling sufficient for single user

**Screening Service:**
- FastAPI endpoints for screen execution
- SQL queries against TimescaleDB
- Screen templates stored in database
- Results ranked and cached
- Export to CSV/JSON

### 5.3 Technology Stack

**Backend:**
- **Primary Language:** Python 3.11+
- **Web Framework:** FastAPI for REST API
- **Task Queue:** Celery with Redis broker
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** scikit-learn, XGBoost, LightGBM
- **Deep Learning:** PyTorch (CUDA support for M2000 GPU)
- **Time Series:** statsmodels, Prophet, ARIMA
- **NLP:** Transformers (FinBERT for sentiment)
- **Technical Analysis:** TA-Lib, pandas-ta
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Testing:** pytest
- **API Documentation:** OpenAPI/Swagger (FastAPI built-in)

**Data Storage:**

**PostgreSQL 15+ with TimescaleDB Extension:**
- Portfolio holdings and transactions
- Stock quotes (hypertable for time-series optimization)
- Screen definitions and results
- Alert configurations
- News articles and sentiment scores
- ML predictions and accuracy tracking
- TFSA contribution tracking
- All application data in single database

**Redis 7:**
- API response caching (24hr TTL for historical data)
- Real-time quote caching (5min TTL during market hours)
- Rate limiting counters (API usage tracking)
- Celery message broker
- Session storage (if auth implemented)
- Temporary computation results

**Docker Volumes:**
- `postgres_data`: PostgreSQL data files
- `redis_data`: Redis persistence (optional)
- `ml_models`: Trained model artifacts
- No object storage needed - local volumes sufficient

**Frontend:**
- **Web Framework:** React 18+ with TypeScript (or FastAPI Jinja2 templates for MVP)
- **State Management:** Zustand (simpler than Redux for single user)
- **UI Components:** Tailwind CSS (utility-first, smaller bundle)
- **Charting:** Lightweight Charts (best for financial data)
- **Data Fetching:** Native fetch with custom hooks (no extra library needed)
- **Build Tool:** Vite (faster than Webpack)
- **Testing:** Vitest, React Testing Library

**Mobile:**
- No native app - responsive web design sufficient
- PWA (Progressive Web App) for mobile-like experience
- Can add to home screen on iOS/Android
- Works offline with service worker caching

**Infrastructure:**
- **Hosting:** Self-hosted dedicated server (Ubuntu 24.04)
- **Containerization:** Docker 24+
- **Orchestration:** Docker Compose (systemd-managed)
- **Scheduling:** Host cron jobs (simpler than Celery Beat)
- **Process Management:** systemd for Docker Compose stack
- **Monitoring:** Prometheus + Grafana (optional Docker Compose profile)
- **Logging:** Docker logs + journald (simple, no ELK needed)
- **Reverse Proxy:** Nginx (Docker container or host-installed)
- **SSL Certificates:** Let's Encrypt via certbot
- **DNS:** Local DNS (server.local) or optional domain with Cloudflare
- **Backup:** Host cron + pg_dump to external drive
- **GPU Runtime:** NVIDIA Docker for ML training

### 5.4 Server Infrastructure

**Actual Hardware Configuration:**

**Dedicated Server:**
- **CPU:** Intel Xeon E3-1240 v5 (4 cores, 8 threads @ 3.5GHz)
- **RAM:** 32GB DDR4
- **Storage:** 500GB (SSD or HDD - to be confirmed)
- **GPU:** NVIDIA Quadro M2000 (4GB VRAM, Maxwell architecture, CUDA 5.2)
- **OS:** Ubuntu 24.04 LTS
- **Network:** Connected to home network as server.local
- **Purpose:** Dedicated to stonk-bro application

**Resource Allocation (32GB RAM):**
- PostgreSQL: 8GB (shared_buffers=2GB, effective_cache_size=6GB)
- Redis: 2GB
- API Service: 2GB
- Celery Worker: 4GB
- Frontend: 512MB
- Nginx: 256MB
- ML Training: 12GB (when active, otherwise freed)
- System + Buffer: 3.5GB

**Storage Strategy:**
- Docker volumes for all persistent data
- External USB/NAS drive for backups (recommended)
- No cloud storage needed (local backups sufficient)
- ~100-200GB expected for 5 years of stock data

**Network Setup:**
- Static IP on local network (recommended)
- Access via http://server.local or static IP
- Optional: Domain with Cloudflare for external access
- Optional: Tailscale/WireGuard VPN for remote access
- No port forwarding needed if VPN-only access

**Docker Compose Stack:**

**Container Registry:**
- Not needed - build images locally
- Images stored on local Docker daemon
- No push/pull from remote registry

**Storage Solutions:**
- **Docker named volumes:** All persistent data
  - `postgres_data` (database files)
  - `redis_data` (optional persistence)
  - `ml_models` (trained model artifacts)
- **Host bind mounts:** Configuration files only
- No distributed storage needed (single server)

**Database Deployment:**
- PostgreSQL + TimescaleDB in Docker container
- Redis in Docker container
- Both use named volumes for persistence
- Automated backups via host cron + pg_dump

**Application Deployment:**
- **Docker Compose** manages all services
- **systemd** manages Docker Compose (auto-start on boot)
- **Host cron** for scheduled tasks
- Simple, reliable, easy to debug

**Reverse Proxy and SSL:**
- Nginx in Docker container (or host-installed)
- Let's Encrypt SSL via certbot
- Routes requests to frontend (port 3000) and API (port 8000)
- Only ports 80/443 exposed to network

**Monitoring:**
- **Basic:** `docker stats` and `docker logs`
- **Optional:** Prometheus + Grafana (Docker Compose profile)
- **System:** Standard Linux tools (htop, iotop, df)
- **Logs:** Docker logs + journald (no separate logging stack)

**Backup Strategy:**
- **Daily:** PostgreSQL dump via cron to external drive
  ```bash
  0 3 * * * docker exec stonk-postgres pg_dump -U stockuser stockdb | gzip > /backups/$(date +\%Y\%m\%d).sql.gz
  ```
- **Weekly:** Docker volume backup
- **Retention:** 7 daily, 4 weekly, 12 monthly
- **Offsite:** Optional external drive at different location
- **No cloud backup needed** (unless desired)

**Networking and Access:**

**Access Options:**
1. **Local Network Only (Simplest):**
   - Access via http://server.local from home network
   - No external access needed
   - Most secure option

2. **VPN Access (Recommended for Remote):**
   - Tailscale (easiest setup, free)
   - WireGuard (more control)
   - Access server from anywhere securely

3. **Public Access (Optional):**
   - Port forwarding 80/443 through router
   - Or Cloudflare Tunnel (no port forwarding needed)
   - Requires domain name and SSL certificate

**Domain and SSL (Optional):**
- Domain optional (can use server.local or IP)
- If using domain: Let's Encrypt via certbot (free)
- Auto-renewal via cron job
- HTTPS recommended even for local network

**Internet Requirements:**
- Standard home internet sufficient
- No high upload speed needed (single user)
- Bandwidth usage minimal (API calls, not streaming)

**Security Considerations:**

**Network Security:**
- Firewall rules (ufw): block all inbound except 80/443 (if public)
- Or VPN-only access (most secure)
- fail2ban optional (not needed if VPN-only)
- Regular Ubuntu security updates (unattended-upgrades)

**Application Security:**
- No authentication needed (single user, private network)
- Or basic HTTP auth if exposed publicly
- SSL/TLS for encrypted transport
- Environment variables for secrets (.env file, not in git)
- Regular Docker image updates

**Physical Security:**
- Standard home security sufficient
- Server in safe, climate-controlled location
- UPS optional for clean shutdowns during power loss

**Power and Cooling:**
- Power consumption: ~150-250W typical for this server
- Annual electricity: ~$100-200 (varies by location)
- UPS optional ($100-200) for graceful shutdown
- Standard case ventilation sufficient
- No special cooling required

**Availability Expectations:**
- Single server = single point of failure (acceptable for personal use)
- No high availability (HA) needed
- Downtime for updates/maintenance is fine
- Target uptime: 95-99% (not 99.9%)
- Can restart services without data loss (persistent volumes)

**Cost Breakdown (Dedicated Server):**

**Hardware Investment:**
- Server: Already owned (Intel Xeon E3-1240 v5, 32GB RAM)
- Storage: Existing 500GB drive
- External backup drive: $50-100 (recommended)
- Optional UPS: $100-200
- **Total: $50-300 (minimal additional investment)**

**Annual Operating Costs:**
- Electricity (~150-250W): $100-200/year
- Internet: $0 (existing home connection)
- Domain registration: $10-15/year (optional)
- **Total: $100-215/year**

**Data and API Costs:**
- Primary: yfinance (FREE - unlimited)
- Supplementary: Alpha Vantage free tier (25 requests/day)
- News: NewsAPI free tier (100 requests/day) + RSS feeds
- **Total: $0/month**

**No External Service Costs:**
- No cloud hosting
- No authentication service (single user, VPN access)
- No managed databases
- No CDN (single user)
- No email service (use personal Gmail SMTP for alerts)

**Total Annual Cost:** $100-215/year

**Value Proposition:**
- Minimal ongoing costs (just electricity)
- Full control over data and infrastructure
- Your financial data stays on your hardware (privacy)
- No recurring subscriptions
- Learn Docker, ML, full-stack development
- Leverage existing hardware investment

### 5.5 Development Workflow

**Local Development:**
- Develop on server directly or separate dev machine
- Docker Compose for running all services locally
- Hot reload for FastAPI (--reload flag)
- React dev server for frontend
- Test database separate from production

**Version Control:**
- Git repository (GitHub or self-hosted Gitea)
- Simple workflow: main branch only (single developer)
- Or: main + dev branches if desired
- Semantic versioning for releases (tags)

**Deployment Process:**
- **Simple:** Git push, SSH to server, `git pull && docker compose up -d --build`
- **Automated (optional):** Git webhook triggers deployment script
- Database migrations via Alembic before deployment
- Zero-downtime not needed (single user)

**Testing Strategy:**
- Unit tests (pytest) for business logic
- Integration tests for API endpoints
- Manual testing sufficient for single user
- Optional: E2E tests with Playwright

**Monitoring:**
- Docker stats for resource usage
- Docker logs for debugging
- Optional: Prometheus + Grafana
- Email alerts for critical errors

**Deployment Simplicity:**
- No CI/CD pipeline needed (manual deploy is fine)
- No blue-green or canary deployments
- No load testing required
- Keep it simple - you're the only user

### 5.6 Data Flow Architecture

**Market Data Pipeline:**
1. Scheduled jobs trigger API requests to data providers
2. Raw data received and validated
3. Data normalized to standard schema
4. Stored in time-series database
5. Update events published to message queue
6. Analysis engine subscribers consume events
7. Calculations performed and results cached
8. Real-time updates pushed to connected clients via WebSocket

**User Request Flow:**
1. Client sends HTTP request to API Gateway
2. Gateway authenticates request and routes to service
3. Service checks cache for recent results
4. On cache miss, retrieves from database
5. Business logic applied and transformations performed
6. Response formatted and returned to client
7. Cache updated for subsequent requests

**Prediction Generation Flow:**
1. Scheduler triggers prediction job for stock universe
2. Feature engineering service fetches required data
3. Features computed and normalized
4. Multiple models generate predictions
5. Ensemble method combines predictions
6. Confidence intervals calculated
7. Results stored in database with timestamp
8. Alerts generated for significant changes
9. Users notified of new predictions

**Alert Processing Flow:**
1. Alert engine polls for data changes
2. User alert rules evaluated against new data
3. Conditions met trigger alert creation
4. Alert deduplicated against recent alerts
5. Notification formatted based on delivery channel
6. Notification sent via email/push/SMS
7. Delivery status tracked
8. Alert history updated

### 5.6 Performance Optimization

**Resource Management:**
- Single user = minimal concurrent load
- 32GB RAM is plenty for all services
- Docker resource limits prevent any service from consuming all RAM
- PostgreSQL gets 8GB (largest allocation)

**Caching Strategy:**
- Redis caching critical for API rate limit conservation
- Historical data: 24-hour TTL
- Real-time quotes: 5-minute TTL during market hours
- Predictions: cached until next model run

**Database Optimization:**
- TimescaleDB for time-series query optimization
- Proper indexes on (symbol, timestamp)
- Continuous aggregates for common queries
- Query optimization for dashboard loads

**ML Training:**
- Run overnight (low resource contention)
- GPU-accelerated when needed (M2000)
- Batch processing, not real-time
- Model artifacts cached in Docker volume

**Data Growth:**
- Storage: ~50-100GB/year for extensive data (1000+ stocks)
- Can track thousands of stocks with 500GB drive
- Old data can be archived if needed

**No Scaling Concerns:**
- Single user = no horizontal scaling needed
- No load balancing
- No database sharding
- Simple architecture, easy to maintain

---

## 6. Data Sources and Integration

### 6.1 Market Data Providers

**Primary Providers:**

**Alpha Vantage:**
- Real-time and historical stock data
- Free tier: 25 requests/day, premium available
- Coverage: US and Canadian exchanges
- Data: Quotes, OHLCV, technical indicators
- API rate limits: 5 requests/minute (free)

**IEX Cloud:**
- US market data with generous free tier
- Real-time quotes (15-minute delay on free)
- Coverage: NYSE, NASDAQ, major indices
- Data: Quotes, historical prices, corporate actions
- API rate limits: 500,000 messages/month (free)

**Yahoo Finance (yfinance Python library):**
- Unofficial API, no official support
- Free, no authentication required
- Coverage: Global exchanges
- Data: Historical prices, fundamentals, options
- Reliability: Can change without notice
- Use as backup/supplementary source

**Financial Modeling Prep:**
- Comprehensive financial data
- Free tier: 250 requests/day
- Coverage: 50,000+ stocks globally
- Data: Fundamentals, analyst estimates, insider trades
- API rate limits: Varies by plan

**Canadian-Specific Sources:**

**TMX Money (TSX/TSXV):**
- Official source for Canadian exchanges
- Free access to delayed data
- Coverage: TSX, TSXV listings
- Data: Quotes, corporate actions, financials

**Questrade API (if user has account):**
- Direct broker integration
- Real-time portfolio synchronization
- Trading capability (future feature)
- Requires user authorization

**Cost Optimization Strategies:**

**Maximize Free Tiers:**
- Rotate between multiple free-tier accounts (Alpha Vantage, Financial Modeling Prep)
- Use yfinance as primary source for historical data (unlimited, free)
- Cache aggressively to minimize API calls
- Batch requests when possible
- Schedule data updates during off-peak times

**Smart Request Management:**
- Prioritize data updates for user watchlist and portfolio stocks
- Update popular stocks more frequently than obscure ones
- Use incremental updates rather than full refreshes
- Implement exponential backoff for rate-limited requests
- Track API usage per day/month to stay within limits

**Data Locality:**
- Store downloaded data locally for extended periods
- Build historical database from one-time bulk downloads
- Only fetch new data (daily updates) after initial population
- Archive old data to reduce active dataset size

**Free Alternative Sources:**
- Yahoo Finance via yfinance library (primary recommendation)
- Pandas DataReader for various free sources
- Web scraping as last resort (be respectful of ToS)
- SEC EDGAR and SEDAR for fundamentals (completely free)
- RSS feeds for news (free with minimal parsing)

**Hybrid Approach:**
- Free sources for historical and fundamental data
- Paid tier only if user base grows significantly
- User-funded API keys (users bring their own)
- Aggregate data across multiple users efficiently

**Realistic Free Tier Capacity:**
- Alpha Vantage: 25 stocks/day, ~750/month
- IEX Cloud: 500K messages/month, ~50-100 stocks daily
- yfinance: Unlimited stocks (use as primary)
- Financial Modeling Prep: 250 stocks/day, ~7,500/month

**Recommended Initial Setup:**
1. Use yfinance as primary data source
2. Alpha Vantage for supplementary data
3. SEC EDGAR/SEDAR for fundamentals
4. NewsAPI + RSS feeds for news
5. Upgrade to paid tiers only when necessary (>100 users)

### 6.2 Fundamental Data Sources

**SEC EDGAR:**
- US company filings (10-K, 10-Q, 8-K, DEF 14A)
- Free public access
- Structured XML data (XBRL format)
- Historical filings archive
- Python libraries: sec-edgar-downloader, edgar-tools

**SEDAR+:**
- Canadian company filings
- Free public access
- Annual and interim financial statements
- Management discussion and analysis
- Prospectuses and offering documents

**Financial APIs:**
- Financial Modeling Prep: Income statements, balance sheets, cash flows
- Alpha Vantage: Company overview, earnings, income statements
- Intrinio: Premium financial data with quality guarantees
- SimFin: Free fundamental data for research

### 6.3 News and Sentiment Data

**News Sources:**
- **NewsAPI:** Aggregates 80,000+ sources, free tier 100 requests/day
- **Finnhub:** Financial news and sentiment, free tier available
- **Alpha Vantage:** News sentiment endpoint
- **RSS Feeds:** Financial Post, Globe and Mail, Seeking Alpha
- **Company Websites:** Investor relations sections, press releases

**Social Media:**
- **Twitter/X API:** Requires paid tier for comprehensive access
- **Reddit API:** Free access to financial subreddits (r/wallstreetbets, r/stocks, r/CanadianInvestor)
- **StockTwits API:** Social sentiment for stocks, free tier available

**Sentiment Analysis:**
- Pre-trained models: FinBERT, Twitter Financial News Sentiment
- Custom fine-tuned models on financial text
- Rule-based sentiment for financial keywords
- Aggregation and weighting of multiple sources

### 6.4 Economic and Market Data

**Interest Rates and Yields:**
- Bank of Canada: Overnight rate, bond yields
- US Federal Reserve: Fed funds rate, treasury yields
- FRED (Federal Reserve Economic Data): Comprehensive economic indicators

**Currency Exchange Rates:**
- Bank of Canada: CAD/USD exchange rates
- Exchange rate APIs for portfolio currency conversion

**Market Indices:**
- S&P/TSX Composite Index
- S&P 500 Index
- Sector indices
- VIX (volatility index)

### 6.5 Data Quality and Management

**Data Validation:**
- Range checks for price and volume data
- Outlier detection and flagging
- Cross-source validation
- Historical consistency checks
- Missing data handling (forward fill, interpolation)

**Data Normalization:**
- Standardized schemas across sources
- Stock symbol mapping (handle ticker changes)
- Timezone conversions to ET/UTC
- Corporate action adjustments (splits, dividends)
- Currency conversions to CAD

**Data Refresh Frequencies:**
- Real-time quotes: 5-15 minute delay (free tier)
- End-of-day prices: Daily after market close
- Fundamental data: Quarterly after earnings
- News: Continuous throughout day
- Predictions: Daily or on significant data changes
- Portfolio valuation: Real-time during market hours

**API Management:**
- Centralized API key storage (secrets manager)
- Rate limit tracking and throttling
- Automatic failover between providers
- Request caching to minimize API calls
- Error handling and retry with exponential backoff
- Usage monitoring and alerts for approaching limits

### 6.6 Data Retention Policies

**Hot Storage (Fast Access):**
- Last 2 years of daily price data
- Last 6 months of intraday data
- Recent news (3 months)
- Current portfolio and holdings
- Active alerts and configurations

**Cold Storage (Archive):**
- Historical price data beyond 2 years
- Old news articles and sentiment
- Closed portfolio positions
- Historical predictions for analysis
- User activity logs

**Data Deletion:**
- User account deletion removes personal data
- Anonymized usage data retained for analytics
- Regulatory compliance with data retention laws

---

## 7. Machine Learning Models

### 7.1 Model Development Process

**Data Preparation:**
1. Feature engineering from raw market data
2. Feature selection using correlation and importance analysis
3. Train/validation/test split (60%/20%/20%)
4. Time-based splitting to avoid look-ahead bias
5. Feature scaling and normalization
6. Handling missing values and outliers

**Model Training:**
1. Baseline model establishment (simple moving average)
2. Individual model training with cross-validation
3. Hyperparameter tuning using grid search or Bayesian optimization
4. Ensemble model creation
5. Model calibration for prediction intervals
6. Out-of-sample testing

**Model Evaluation:**
- Regression metrics: MAE, RMSE, MAPE
- Classification metrics: Accuracy, precision, recall (for direction prediction)
- Financial metrics: Sharpe ratio, maximum drawdown
- Backtesting on historical data
- Walk-forward analysis for robustness
- Comparison against buy-and-hold benchmark

**Model Deployment:**
- Model serialization (pickle, joblib, ONNX)
- Version control with MLflow or similar
- A/B testing infrastructure
- Canary deployments for new models
- Rollback capability for model issues

**Model Monitoring:**
- Prediction vs. actual tracking
- Model drift detection
- Feature distribution monitoring
- Performance degradation alerts
- Automated retraining triggers

### 7.2 Feature Engineering

**Price-Based Features:**
- Returns over multiple periods (1-day, 5-day, 20-day, 60-day)
- Log returns for stationarity
- Price momentum and acceleration
- Gap up/down from previous close
- Intraday range (high-low spread)
- Close relative to range position

**Volume-Based Features:**
- Volume relative to average
- Volume rate of change
- On-Balance Volume (OBV)
- Volume-price trends
- Accumulation/distribution indicators

**Technical Indicator Features:**
- Moving averages (SMA, EMA) for multiple periods
- MACD line, signal line, histogram
- RSI values
- Stochastic oscillator
- Bollinger Band position and width
- ATR for volatility
- ADX for trend strength

**Fundamental Features:**
- P/E ratio, P/B ratio, P/S ratio
- ROE, ROA, profit margins
- Debt ratios
- Earnings growth rates
- Cash flow metrics
- Dividend yield
- Piotroski F-Score

**Market Context Features:**
- Sector index returns
- Market index (S&P 500, TSX) returns
- VIX level and changes
- Correlation to market
- Beta coefficient
- Market cap decile

**Sentiment Features:**
- News sentiment score (aggregated)
- Social media sentiment
- News volume and velocity
- Analyst recommendation changes
- Insider transaction signals

**Time Features:**
- Day of week
- Month of year
- Days until earnings
- Seasonality indicators
- Market regime (bull/bear/sideways)

**Derived Features:**
- Feature interactions (e.g., momentum × volatility)
- Lagged features (t-1, t-5, t-20)
- Rolling statistics (mean, std, min, max)
- Rate of change features
- Divergence between indicators

### 7.3 Model Architecture Details

**ARIMA Models:**
- Auto ARIMA for parameter selection
- Seasonal ARIMA (SARIMA) for seasonality
- Used for short-term predictions (1-7 days)
- Handles trends and seasonality well
- Fast training and inference
- Good baseline model

**Random Forest:**
- Ensemble of 100-500 decision trees
- Max depth: 10-20 to prevent overfitting
- Feature importance analysis built-in
- Handles non-linear relationships
- Robust to outliers
- Used for medium-term predictions (1-3 months)

**Gradient Boosting (XGBoost):**
- Sequential tree building
- Learning rate: 0.01-0.1
- Max depth: 3-8
- Early stopping based on validation loss
- Excellent performance on tabular data
- Feature importance via gain
- Used for all prediction horizons

**LSTM Neural Networks:**
- 2-3 LSTM layers with 50-100 units each
- Dropout layers (0.2-0.3) for regularization
- Dense output layer for price prediction
- Input sequence length: 20-60 days
- Trained with Adam optimizer
- Learning rate scheduling
- Used for long-term predictions (6-12 months)

**Transformer Models:**
- Attention mechanism for sequential data
- Positional encoding for time information
- Multi-head attention (4-8 heads)
- Feed-forward layers
- Experimental, high computational cost
- Best for complex temporal patterns

**Ensemble Strategy:**
- Weighted average based on historical accuracy
- Dynamic weights adjusted monthly
- Simple average for initial deployment
- Stacking with meta-learner (linear regression or gradient boosting)
- Model selection based on prediction horizon

### 7.4 Model Retraining Schedule

**Frequency:**
- Daily incremental updates for recent data
- Weekly full retraining for short-term models
- Monthly full retraining for long-term models
- Quarterly comprehensive model review and architecture updates

**Triggers for Immediate Retraining:**
- Model accuracy drops below threshold (MAPE > 15%)
- Market regime change detected
- Significant corporate events (mergers, splits)
- Data quality issues resolved
- New features available

**Retraining Process:**
1. Fetch latest training data (rolling window)
2. Validate data quality
3. Engineer features with new data
4. Train models with cross-validation
5. Evaluate on hold-out test set
6. Compare to existing model performance
7. Deploy if improvement > 5% in accuracy
8. Log model metrics and version

### 7.5 Prediction Confidence and Uncertainty

**Confidence Intervals:**
- 80%, 90%, 95% intervals from model uncertainty
- Quantile regression for prediction intervals
- Bootstrap resampling for uncertainty estimates
- Ensemble spread as confidence proxy

**Uncertainty Sources:**
- Model uncertainty (different models, different predictions)
- Data uncertainty (noisy input data)
- Parameter uncertainty (hyperparameter sensitivity)
- Aleatoric uncertainty (inherent randomness in markets)

**Confidence Score:**
- Composite score from multiple factors
- Historical model accuracy
- Prediction consensus across models
- Input data quality
- Market volatility level
- Prediction horizon (longer = lower confidence)

**Communication to Users:**
- Visual representation of confidence bands
- Explicit statement of uncertainty
- Scenario analysis (bull/base/bear cases)
- Disclaimer about prediction limitations

### 7.6 Ethical Considerations

**Transparency:**
- Clearly communicate that predictions are probabilistic
- Explain model limitations and failure modes
- Provide insight into prediction drivers (feature importance)
- No guarantees of future performance

**Bias Mitigation:**
- Regular audits for systematic prediction biases
- Check for sector or cap-size biases
- Ensure training data represents diverse market conditions
- Avoid overfitting to recent market regimes

**Responsible AI:**
- Models are decision support tools, not trading bots
- Human oversight encouraged for all investment decisions
- Risk management features prominent in UI
- Educational content on model interpretation

---

## 8. User Interface Design

### 8.1 Design Principles

**Clarity:**
- Clean, uncluttered layouts
- Clear visual hierarchy
- Consistent terminology
- Progressive disclosure of complexity

**Efficiency:**
- Quick access to key information
- Minimal clicks to common actions
- Keyboard shortcuts for power users
- Customizable dashboards

**Responsiveness:**
- Fast page loads (<2 seconds)
- Real-time data updates
- Optimistic UI updates
- Loading states and skeleton screens

**Accessibility:**
- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- Color blindness considerations
- High contrast mode

**Mobile-First:**
- Responsive design for all screen sizes
- Touch-friendly controls
- Simplified mobile navigation
- Native mobile app experience

### 8.2 Key Screens and Features

**Dashboard (Home Page):**

Components:
- Portfolio summary card (value, daily change, total return)
- Market indices widget (TSX, S&P 500)
- Top gainers/losers in portfolio (table)
- Recent alerts (list with action buttons)
- News feed (relevant to portfolio)
- Quick actions (add position, run screen, view watchlist)

Customization:
- Widget arrangement via drag-and-drop
- Show/hide widgets
- Widget refresh rates
- Theme selection (light/dark)

**Portfolio View:**

Tabs:
- Holdings: All current positions with key metrics
- Performance: Charts and analytics
- Transactions: History of buys/sells
- Analysis: Risk metrics and allocation

Holdings Table Columns:
- Symbol and company name
- Quantity and average cost
- Current price and change
- Market value
- Gain/loss ($ and %)
- Allocation (%)
- Actions (sell, add, view details)

Performance Charts:
- Portfolio value over time (line chart)
- Returns by period (bar chart)
- Allocation breakdown (pie/donut chart)
- Comparison to benchmarks (multi-line chart)

**Stock Detail Page:**

Sections (tabs or vertical layout):
- **Overview:** Current price, key stats, company description
- **Chart:** Interactive price chart with indicators
- **Fundamentals:** Financial metrics and statements
- **Technicals:** Indicator values and signals
- **Predictions:** Price forecasts with confidence
- **News:** Recent news and sentiment
- **Analysis:** Peer comparison and ratings

Actions:
- Add to watchlist/portfolio
- Set alert
- View full company profile
- Export data
- Share (link generation)

**Screener Interface:**

Sections:
- Filter Configuration Panel (left sidebar)
  - Fundamental filters with range sliders
  - Technical filters with dropdowns
  - Market filters with checkboxes
- Results Table (main area)
  - Sortable columns
  - Inline mini-charts
  - Relevance score
  - Quick actions (add to watchlist, view details)
- Saved Screens (top bar)
  - Quick load of templates
  - Save current screen
  - Schedule screen runs

Workflow:
1. User selects filters
2. Click "Run Screen"
3. Results load with animation
4. User sorts and reviews results
5. Click on stock to view detail modal
6. Add interesting stocks to watchlist
7. Save screen for future use

**Watchlist View:**

Layout:
- Multiple watchlists in tabs or dropdown
- Compact list view with expandable rows
- Real-time price tickers
- Color-coded changes (green/red)
- Sparkline charts for each stock

Actions per Stock:
- View detailed analysis
- Set alert
- Move to portfolio (simulate buy)
- Remove from watchlist
- Add notes/tags

**Alerts Management:**

Sections:
- Active Alerts (list with toggle on/off)
- Alert History (past triggered alerts)
- Create New Alert (wizard interface)

Alert Creation Flow:
1. Select stock or portfolio-wide
2. Choose condition type (price, technical, news)
3. Set parameters (thresholds, comparisons)
4. Select notification method (email, push, SMS)
5. Name and save alert

Alert Display:
- Notification center icon with badge count
- Alert list with timestamp and details
- Action buttons (view stock, dismiss, snooze)
- Mark all as read option

**Settings Page:**

Sections:
- **Preferences:** Display settings, currency (CAD/USD), theme, date format, default charts
- **TFSA Settings:** Contribution room, birth year, historical contributions
- **Notifications:** Email preferences for each alert type, frequency
- **Data Sources:** API key configuration, data refresh schedules
- **System:** Backup configuration, maintenance schedules
- **Export:** Backup all data, export portfolio history

**Mobile App Specific:**

Features:
- Bottom navigation bar (Dashboard, Portfolio, Screener, Alerts, More)
- Swipe gestures for navigation
- Biometric authentication (Face ID, fingerprint)
- Offline mode with cached data
- Push notification support
- Quick widgets for iOS/Android home screen

### 8.3 Data Visualization Best Practices

**Charts:**
- Use appropriate chart types (line for time series, bar for comparisons, pie for composition)
- Consistent color scheme (green for positive, red for negative)
- Interactive tooltips on hover
- Zoom and pan capability for detailed analysis
- Export chart as image option

**Tables:**
- Sortable columns
- Filterable rows
- Conditional formatting (heatmaps for performance)
- Pagination for large datasets
- Export to CSV/Excel

**Indicators:**
- Clear labels and units
- Comparison to previous period (arrows, percentages)
- Visual cues for thresholds (color changes)
- Tooltips with explanations

---

## 9. Security and Compliance

### 9.1 Security Measures (Single User - Simplified)

**Authentication:**
- Basic HTTP authentication sufficient for personal use
- Optional: OAuth with personal Google/GitHub account
- VPN access (Tailscale/WireGuard) for remote access (recommended)
- Strong password for web interface
- Optional: 2FA for additional security

**Authorization:**
- Not needed - single user has full access
- Simple admin interface without role management

**Data Security:**
- Encryption at rest optional (LUKS for drives if desired)
- Encryption in transit (TLS 1.3 via Let's Encrypt)
- API keys stored in environment variables or secrets file
- No sensitive financial credentials stored (read-only data)

**Application Security:**
- Basic input validation
- SQL injection prevention (use ORMs with parameterized queries)
- Keep dependencies updated
- Firewall rules (only expose necessary ports)
- Optional: Fail2ban for brute force protection

**Infrastructure Security:**
- Firewall on router (only forward necessary ports)
- Keep systems patched and updated
- Regular security updates for OS and containers
- Optional: Separate VLAN for homelab

**Physical Security:**
- Standard home security (locked house)
- Consider encrypted drives for sensitive data
- Regular backups to prevent data loss

**Privacy:**
- Your data stays on your hardware
- No third-party access
- Only external API calls are for market data (public information)

**Simplified Approach:**
- Use Cloudflare Tunnel - no port forwarding needed, built-in security
- Or use Tailscale VPN - access only from your devices
- Basic auth + HTTPS sufficient for personal platform
- Focus on backup and disaster recovery over complex security

### 9.2 Regulatory Compliance (Personal Use)

**Canadian Securities Regulations:**
- Personal investment tool - no regulatory requirements
- Not providing advice to others
- Not operating as a business
- No licensing or registration needed for personal use

**TFSA Compliance:**
- Track your own contribution room accurately
- Ensure investments are TFSA-qualified
- Be aware of foreign withholding tax on US dividends
- Avoid day trading patterns that could trigger CRA scrutiny
- Platform helps track and manage TFSA rules

**Data Regulations:**
- PIPEDA not applicable (personal use, not collecting others' data)
- Your own data privacy under your control
- No external data sharing

**Disclaimers (For Yourself):**
- Remember: Investment involves risk
- Past performance doesn't guarantee future results
- ML predictions are estimates with uncertainty
- Consider consulting a qualified advisor for major decisions
- Models are tools to support your judgment, not replace it

**No Terms of Service Needed:**
- Personal platform for your own use
- No liability concerns
- No user agreements needed

### 9.3 Monitoring and Logging (Personal Use - Simplified)

**Application Logging:**
- Basic application logs for debugging
- Error tracking and exception logs
- Trade decision logs for personal review
- Model prediction logs for accuracy tracking
- Optional: Structured logging with JSON format

**System Monitoring:**
- Resource usage (CPU, RAM, disk, network)
- Service health checks
- Database performance
- API rate limit tracking
- Simple dashboard (Grafana or Netdata)

**Alerts (For You):**
- System down alerts (email or mobile notification)
- Disk space warnings
- Database backup failures
- API rate limit approaching
- Model training failures

**Log Retention:**
- Keep recent logs (30-90 days) for troubleshooting
- Archive or delete old logs to save space
- No compliance requirements, keep what's useful

**Tools:**
- Simple: tail -f logs, systemd journal
- Intermediate: Loki + Grafana
- Optional: ELK stack if you want to learn it

**Backup Verification:**
- Automated backup success/failure notifications
- Periodic restore testing
- Checksum verification

---

## 10. TFSA-Specific Features

### 10.1 TFSA Education

**In-App Guide:**
- What is a TFSA and how it works
- Contribution limits and rules
- Qualified investments
- Benefits of tax-free growth
- Common mistakes to avoid
- Strategies for maximizing TFSA

**Contextual Help:**
- Tooltips explaining TFSA concepts
- Links to CRA resources
- FAQ section
- Glossary of terms

### 10.2 Contribution Room Tracking

**Features:**
- Manual entry of current contribution room
- Automatic adjustment for contributions and withdrawals
- Annual contribution limit updates (January 1)
- Carry-forward of unused room
- Visualization of available room
- Alerts when room is available or nearly exhausted

**Calculation:**
```
Current Room = Previous Year Room + Annual Limit + Withdrawals - Contributions
```

**Data Inputs:**
- User's birth year (to determine when eligible)
- Cumulative contribution history
- Withdrawal history
- Current calendar year

**Validation:**
- Warning if user enters contribution exceeding available room
- Historical contribution limits by year reference table
- Link to CRA website for verification

### 10.3 Qualified Investment Checker

**Purpose:** Help users ensure investments are TFSA-qualified

**TFSA Qualified Investments (generally):**
- Stocks listed on designated exchanges (TSX, TSXV, NYSE, NASDAQ, etc.)
- Mutual funds and ETFs
- Bonds and GICs
- Canadian cash and savings accounts

**Non-Qualified or Restricted:**
- Private company shares (not publicly traded)
- Shares of companies user has significant control over
- Certain foreign investments
- Exempt market securities (some)

**Feature:**
- Indicator on stock detail page (checkmark or warning)
- Filter in screener for TFSA-qualified only
- Portfolio review for non-qualified holdings
- Educational notes on why certain investments may not qualify

### 10.4 Foreign Withholding Tax Information

**US Dividend Tax:**
- US stocks in TFSA subject to 15% withholding tax on dividends
- Non-recoverable in TFSA (unlike RRSP)
- Displayed in dividend tracking
- Educational note explaining the impact
- Consideration in yield calculations

**Example Display:**
- Gross dividend: $100
- Withholding tax (15%): $15
- Net dividend received: $85
- Effective yield: Adjusted for withholding

### 10.5 TFSA Strategy Tools

**Contribution Optimizer:**
- Suggests optimal timing for contributions
- Considers market conditions and seasonal patterns
- Dollar-cost averaging calculator
- Lump sum vs. periodic contribution analysis

**Rebalancing Guidance:**
- Tax-free rebalancing advantage highlighted
- Suggested rebalancing transactions
- No tax loss harvesting in TFSA (not applicable)

**Withdrawal Planning:**
- Impact of withdrawal on future contribution room
- Timing considerations (withdraw late in year if possible)
- Emergency fund vs. TFSA strategy

---

## 11. Performance Metrics

### 11.1 System Performance (Personal Use)

**Response Time:**
- Dashboard load time < 2 seconds
- Chart rendering < 1 second
- Stock search results < 500ms
- ML predictions: minutes to hours (overnight acceptable)

**Availability:**
- Target: Personal convenience (doesn't need 24/7 uptime)
- Acceptable: 95-99% for learning environment
- Maintenance windows as needed
- Can take services down for updates without impact

**Capacity:**
- Support your trading activity and research needs
- Handle hundreds of stocks in portfolio/watchlist
- Process thousands of API requests daily
- Store years of historical data

**Data Freshness:**
- Market data: Daily updates sufficient (after market close)
- Optional: 15-minute delayed data during trading hours
- News: Updated 1-4 times daily (or as you check)
- Predictions: Updated daily or weekly
- Fundamental data: Updated quarterly after earnings

**Performance Monitoring:**
- Track page load times
- Monitor API response times
- Database query performance
- ML model training duration
- Disk space and resource usage

### 11.2 Prediction Performance

**Target Metrics:**
- MAPE < 10% for 1-week predictions
- MAPE < 15% for 1-month predictions
- MAPE < 20% for 3-month predictions
- Directional accuracy > 60% (better than random)
- Sharpe ratio of predicted returns > 0.5

**Benchmark Comparison:**
- Compare to naive baseline (last price)
- Compare to simple moving average
- Compare to analyst consensus estimates
- Track relative performance over time

**Model Monitoring:**
- Daily accuracy reports
- Alert if accuracy drops > 5 percentage points
- Per-stock and per-sector breakdown
- Error analysis and pattern identification

### 11.3 Personal Usage Metrics

**Feature Utilization Tracking:**
- Track which features you use most
- Identify underutilized capabilities
- Optimize frequently-used workflows
- Remove or improve unused features

**Research Efficiency:**
- Time spent on investment research before/after platform
- Number of stocks analyzed per session
- Quality of investment decisions (track for learning)
- Alert relevance and actionability

**Investment Performance:**
- Portfolio returns vs. benchmarks (S&P/TSX, S&P 500)
- Win rate on trades
- Average holding period
- Contribution of platform insights to decisions

**Platform Effectiveness:**
- Prediction accuracy over time
- Alert false positive rate
- Time from alert to action
- Number of investment ideas discovered through screening

**Personal Satisfaction:**
- Does the platform make investing easier?
- Are you learning from the analytics?
- Is the time investment in building/maintaining worthwhile?
- What features add most value?

---

## 12. Implementation Roadmap

### 12.1 Phase 1: MVP (Months 1-3)

**Core Features:**
- Portfolio tracking (manual entry)
- Basic stock screener (fundamental filters)
- Stock detail pages with key metrics
- Simple price charts with technical indicators
- Email alerts for price changes
- TFSA contribution room tracking
- Responsive web interface

**Data:**
- Daily price data from yfinance (free, unlimited)
- Basic fundamental metrics from yfinance and Alpha Vantage
- End-of-day data refresh via cron job

**Infrastructure:**
- Single workstation or Docker Compose setup
- PostgreSQL + TimescaleDB database
- Redis caching
- Basic monitoring (Netdata or Grafana)
- Simple backup script

**Success Criteria:**
- Can track your portfolio in real-time
- Screener finds investment opportunities
- Alerts work reliably
- Dashboard loads quickly
- Data updates daily without intervention

### 12.2 Phase 2: Enhanced Analytics (Months 4-6)

**New Features:**
- Advanced technical analysis indicators (RSI, MACD, Bollinger Bands)
- Advanced screening (technical + fundamental combined)
- Watchlist management with multiple lists
- News aggregation from RSS feeds and NewsAPI
- Web and email notifications
- Performance analytics and charts
- Benchmark comparison (vs. indices)

**Improvements:**
- Faster data updates (multiple times per day)
- Better error handling and retry logic
- Improved UI/UX based on your experience
- Mobile-responsive design

**Data:**
- Intraday data for tracked stocks (if desired)
- News from RSS feeds and NewsAPI free tier
- Basic sentiment analysis on news

**Infrastructure:**
- Migrate to k3s if desired (or stay with Docker Compose)
- Add message queue (Redis Streams or RabbitMQ)
- Celery for background jobs
- Enhanced monitoring dashboards

**Success Criteria:**
- Using platform daily for market research
- Technical analysis informs trading decisions
- News alerts actionable and timely
- System runs reliably without daily intervention

### 12.3 Phase 3: Predictions and ML (Months 7-9)

**New Features:**
- Price prediction models (1-week, 1-month, 3-month horizons)
- Multiple ML models (ARIMA, Random Forest, LSTM)
- Prediction confidence intervals
- Model accuracy tracking and visualization
- Historical prediction archive
- Backtesting framework for strategies

**Models:**
- Start with ARIMA for simplicity
- Add Random Forest for robust predictions
- LSTM if GPU available and you want to learn deep learning
- Ensemble predictions combining multiple models

**Data:**
- Historical data backfill (5-10 years)
- Feature engineering pipeline
- Model training automation (weekly retraining)

**Infrastructure:**
- Add GPU if training deep learning models (or use Google Colab)
- MinIO for storing model artifacts
- MLflow or DVC for model versioning
- Jupyter notebooks for experimentation

**Success Criteria:**
- Models generate predictions daily
- Prediction accuracy within target ranges (MAPE < 15%)
- Use predictions as one input to investment decisions
- Understand which models work best for which stocks

### 12.4 Phase 4: Polish and Advanced Features (Months 10-12)

**New Features:**
- Mobile-responsive web app (PWA)
- Advanced charting tools (TradingView-style)
- Export and reporting features (PDF, Excel)
- Broker integration for automatic portfolio sync (Questrade API)
- Options analysis (if interested)
- Sector rotation analysis
- Correlation heatmaps

**Infrastructure:**
- Optimize performance based on usage patterns
- Implement proper backup rotation
- Add redundancy if desired
- Consider Progressive Web App for mobile

**Success Criteria:**
- Platform feels polished and professional
- All major features working smoothly
- Reliable and low-maintenance
- Actively using for investment decisions
- Provides clear value vs. manual research

### 12.5 Ongoing: Maintenance and Improvement

**Continuous Activities:**
- Weekly model retraining
- Data source reliability monitoring
- Security updates and patches
- Feature refinement based on experience
- Add new indicators or analysis as you learn
- Optimize slow queries or pages
- Database maintenance and cleanup
- Backup verification and testing

**Learning Opportunities:**
- Experiment with new ML models
- Try different prediction techniques
- Build custom indicators
- Integrate new data sources
- Improve visualization and UX
- Learn Kubernetes if starting with Docker Compose

### 12.6 Optional Features (Build As Needed)

**Can Skip or Simplify:**
- User authentication (use simple HTTP basic auth or VPN access)
- Multi-user support (not needed)
- Real-time intraday data (end-of-day sufficient for most strategies)
- Mobile app (responsive web app works fine)
- SMS alerts (email sufficient)
- Social features (no other users)
- Complex CI/CD (manual deployment acceptable for personal use)
- Extensive monitoring (simple health checks sufficient)

**Nice to Have (Add Later):**
- Broker integration for automatic sync
- Options analysis and pricing
- Cryptocurrency tracking
- International exchanges beyond US/Canada
- Advanced backtesting framework
- Custom strategy builder
- Earnings calendar integration
- Insider transaction tracking

**Keep It Simple:**
- Focus on features that directly improve your investment decisions
- Don't over-engineer for theoretical future needs
- Build what you'll actually use
- Iterate based on real usage patterns
- Technical learning should be secondary to investment value

---
- Security patches and updates
- User support and feedback integration
- Feature refinement based on usage data
- Compliance with regulatory changes
- Performance optimization
- Content and educational material updates

---

## 13. Risk Management

### 13.1 Investment Risks (User-Facing)

**Market Risk:**
- Systematic risk affecting all investments
- Sector-specific risk concentrations
- Portfolio diversification recommendations
- Beta and correlation tracking

**Liquidity Risk:**
- Identification of thinly traded stocks
- Bid-ask spread monitoring
- Warning for low-volume positions

**Volatility Risk:**
- Historical volatility metrics
- Implied volatility from options (future)
- Position sizing recommendations
- Stop-loss suggestions

**Concentration Risk:**
- Portfolio allocation limits
- Alerts for overconcentration
- Sector and stock limits
- Geographic exposure monitoring

**Model Risk:**
- Prediction uncertainty communication
- Multiple model comparison
- Backtesting results disclosure
- Limitations clearly stated

**Risk Mitigation Features:**
- Portfolio risk score calculation
- Stress testing scenarios
- Diversification analysis
- Position sizing calculator
- Risk/reward ratio for trades
- Educational content on risk management

### 13.2 Technical Risks

**Data Risks:**
- **API Downtime:** Multiple data provider fallbacks, cached data serving
- **Data Quality Issues:** Validation checks, anomaly detection, manual review process
- **API Rate Limits:** Rate limit monitoring, request throttling, upgrade to paid tiers
- **Data Licensing:** Compliance with terms of service, appropriate attribution

**System Risks:**
- **Server Downtime:** Load balancing, redundancy, automated failover
- **Database Failures:** Regular backups, replication, disaster recovery plan
- **Scaling Issues:** Horizontal scaling capability, performance testing
- **Security Breaches:** Encryption, monitoring, incident response plan

**Dependency Risks:**
- **Third-Party Services:** Vendor diversification, critical path identification
- **Library Vulnerabilities:** Regular updates, security scanning
- **Cloud Provider Issues:** Multi-region deployment, backup providers

**Mitigation Strategies:**
- Comprehensive monitoring and alerting
- Regular testing (unit, integration, load)
- Documentation and runbooks
- On-call rotation for critical issues
- Regular backups and disaster recovery drills
- Security audits and penetration testing

### 13.3 Business Risks

**Regulatory Risk:**
- Changes to securities laws affecting app features
- TFSA rule changes requiring updates
- Data privacy law evolution
- Mitigation: Legal consultation, regulatory monitoring

**Competition Risk:**
- Established players (brokerage platforms, Bloomberg, etc.)
- New entrants with better features or pricing
- Mitigation: Continuous innovation, user feedback, unique value proposition

**User Adoption Risk:**
- Insufficient user growth
- High churn rate
- Mitigation: Marketing, user education, feature development, community building

**Monetization Risk:**
- Inability to convert free users to paid
- Pricing model not sustainable
- Mitigation: Value demonstration, flexible pricing, premium feature development

**Reputational Risk:**
- Inaccurate predictions leading to losses
- System failures during critical times
- Negative publicity or reviews
- Mitigation: Transparent communication, disclaimers, excellent support, continuous improvement

---

## 14. Appendices

### Appendix A: Glossary of Terms

**Technical Terms:**
- **ARIMA:** AutoRegressive Integrated Moving Average, a statistical model for time series forecasting
- **LSTM:** Long Short-Term Memory, a type of recurrent neural network for sequential data
- **MAPE:** Mean Absolute Percentage Error, a measure of prediction accuracy
- **Sharpe Ratio:** Risk-adjusted return metric
- **Beta:** Measure of stock volatility relative to market

**Financial Terms:**
- **TFSA:** Tax-Free Savings Account, Canadian tax-advantaged investment account
- **P/E Ratio:** Price-to-Earnings ratio, valuation metric
- **RSI:** Relative Strength Index, momentum indicator
- **MACD:** Moving Average Convergence Divergence, trend-following indicator
- **Market Cap:** Market Capitalization, total value of company's outstanding shares

**Exchange Abbreviations:**
- **TSX:** Toronto Stock Exchange (Canadian large-cap)
- **TSXV:** TSX Venture Exchange (Canadian small-cap)
- **NYSE:** New York Stock Exchange
- **NASDAQ:** National Association of Securities Dealers Automated Quotations

### Appendix B: Docker Compose Deployment

See CLAUDE.md for complete docker-compose.yml example with:
- PostgreSQL + TimescaleDB with resource limits
- Redis with memory limits
- FastAPI backend
- Celery worker for background tasks
- ML trainer with GPU support (optional profile)
- React frontend
- Nginx reverse proxy
- Optional Prometheus + Grafana monitoring

**Quick Start:**
```bash
# Clone repository
git clone <repo-url>
cd stonk-bro

# Create .env file
cp .env.example .env
# Edit .env with your API keys and passwords

# Start core services
docker compose up -d

# Start with monitoring (optional)
docker compose --profile monitoring up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Access application
# - Frontend: http://server.local or http://<server-ip>
# - API: http://server.local:8000/docs
# - Grafana (if monitoring): http://server.local:3001
```

**Production Deployment:**
```bash
# Set up systemd service for auto-start
sudo cp systemd/stonk-bro.service /etc/systemd/system/
sudo systemctl enable stonk-bro
sudo systemctl start stonk-bro

# Set up cron jobs for scheduled tasks
crontab -e
# Add cron jobs from CLAUDE.md

# Set up backup cron
0 3 * * * /home/user/stonk-bro/scripts/backup.sh
```

### Appendix C: API Endpoints (Sample)

**Authentication:**
- POST /api/v1/auth/login (optional - can use basic auth)
- POST /api/v1/auth/logout

**Portfolio:**
- GET /api/v1/portfolio
- POST /api/v1/portfolio/positions
- PUT /api/v1/portfolio/positions/{id}
- DELETE /api/v1/portfolio/positions/{id}
- GET /api/v1/portfolio/performance

**Stocks:**
- GET /api/v1/stocks/{symbol}
- GET /api/v1/stocks/{symbol}/quote
- GET /api/v1/stocks/{symbol}/fundamentals
- GET /api/v1/stocks/{symbol}/technicals
- GET /api/v1/stocks/{symbol}/predictions
- GET /api/v1/stocks/{symbol}/news

**Screening:**
- POST /api/v1/screen/run
- GET /api/v1/screen/saved
- POST /api/v1/screen/save
- DELETE /api/v1/screen/{id}

**Alerts:**
- GET /api/v1/alerts
- POST /api/v1/alerts
- PUT /api/v1/alerts/{id}
- DELETE /api/v1/alerts/{id}

### Appendix D: Database Schema (High-Level)

**Users Table:**
- user_id (PK)
- email (unique)
- password_hash
- created_at
- last_login

**Portfolios Table:**
- portfolio_id (PK)
- user_id (FK)
- name
- type (TFSA, RRSP, non-registered)
- created_at

**Positions Table:**
- position_id (PK)
- portfolio_id (FK)
- symbol
- quantity
- average_cost
- purchase_date
- current_price (cached)

**Watchlists Table:**
- watchlist_id (PK)
- user_id (FK)
- name
- created_at

**Watchlist_Items Table:**
- watchlist_id (FK)
- symbol
- added_at

**Alerts Table:**
- alert_id (PK)
- user_id (FK)
- symbol
- condition_type
- condition_params (JSON)
- notification_method
- is_active
- created_at

**Screens Table:**
- screen_id (PK)
- user_id (FK)
- name
- filters (JSON)
- created_at
- last_run

**Stock_Quotes Table (TimescaleDB):**
- symbol
- timestamp
- open, high, low, close
- volume
- adjusted_close

**Predictions Table:**
- prediction_id (PK)
- symbol
- horizon (days)
- predicted_price
- confidence_low, confidence_high
- model_version
- created_at

**News_Articles Table:**
- article_id (PK)
- symbol (FK, nullable)
- headline
- content
- source
- sentiment_score
- published_at
- fetched_at

### Appendix E: Third-Party Services

**Required:**
- Market Data API (Alpha Vantage, IEX Cloud)
- Email Service (SendGrid, AWS SES)
- Cloud Hosting (AWS, GCP, Azure)
- Domain and SSL Certificates

**Optional:**
- SMS Notifications (Twilio)
- Advanced Charting (TradingView)
- Premium Data Feeds
- ML Model Hosting (AWS SageMaker)

### Appendix F: Compliance Checklist (Simplified for Personal Use)

- [ ] TFSA contribution limits programmed correctly
- [ ] Data encryption in transit (HTTPS)
- [ ] Regular backups configured and tested
- [ ] API keys stored securely (not in code)
- [ ] Strong passwords for web interface
- [ ] Firewall configured on router
- [ ] System updates automated
- [ ] Disclaimer noted that predictions are probabilistic

### Appendix G: Resources and References

**Canadian Resources:**
- Canada Revenue Agency (CRA): TFSA information and contribution limits
- Canadian Securities Administrators (CSA): Securities regulations
- Toronto Stock Exchange: Listing requirements and data
- SEDAR+: Company filings

**Technical Resources:**
- scikit-learn documentation for machine learning
- TensorFlow/PyTorch tutorials for deep learning
- pandas documentation for data manipulation
- FastAPI documentation for API development
- React documentation for frontend development

**Financial Resources:**
- Investopedia: Educational content and definitions
- Yahoo Finance: Market data and news
- Financial Modeling Prep: API documentation
- Alpha Vantage: API documentation

**Books and Papers:**
- "Advances in Financial Machine Learning" by Marcos López de Prado
- "Machine Learning for Asset Managers" by Marcos López de Prado
- "Algorithmic Trading" by Ernest P. Chan
- Academic papers on financial prediction and sentiment analysis

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-06 | Initial Draft | Complete specification created |

---

## Approval and Sign-Off

**Prepared by:** [Your Name]  
**Date:** January 6, 2026  
**Status:** Draft for Review

---

**Note:** This specification document is a living document and will be updated as the project evolves, requirements change, and feedback is incorporated. All stakeholders should review and provide input before development begins.
