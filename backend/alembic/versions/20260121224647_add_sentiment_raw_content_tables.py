"""Add sentiment and raw content tables

Revision ID: 20260121224647
Revises: add_news_alerts
Create Date: 2026-01-21 22:46:47

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260121224647'
down_revision = 'add_news_alerts'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stocks reference table
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index('idx_stocks_symbol', 'stocks', ['symbol'], unique=False)

    # Create scraped_sources configuration table
    op.create_table(
        'scraped_sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column('identifier', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('priority', sa.Integer(), server_default='5', nullable=True),
        sa.Column('min_interval_minutes', sa.Integer(), server_default='60', nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('min_karma', sa.Integer(), nullable=True),
        sa.Column('min_followers', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_items_scraped', sa.BigInteger(), server_default='0', nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), server_default='0', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scraped_sources_active', 'scraped_sources', ['is_active', 'source_type'], unique=False)
    op.create_index('idx_scraped_sources_type_id', 'scraped_sources', ['source_type', 'identifier'], unique=True)

    # Create raw_content table for scraped data
    op.create_table(
        'raw_content',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('author_karma', sa.Integer(), nullable=True),
        sa.Column('author_followers', sa.Integer(), nullable=True),
        sa.Column('author_account_age_days', sa.Integer(), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=True),
        sa.Column('downvotes', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        sa.Column('retweets', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('subreddit', sa.String(length=100), nullable=True),
        sa.Column('is_comment', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('parent_id', sa.String(length=255), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_raw_content_collected', 'raw_content', ['collected_at'], unique=False)
    op.create_index('idx_raw_content_source_collected', 'raw_content', ['source', 'collected_at'], unique=False)
    op.create_index('idx_raw_content_source_id', 'raw_content', ['source', 'source_id'], unique=False)
    op.create_index(
        'idx_raw_content_unprocessed',
        'raw_content',
        ['processed'],
        unique=False,
        postgresql_where=sa.text('processed = false')
    )

    # Create content_stock_mentions junction table
    op.create_table(
        'content_stock_mentions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('content_id', sa.BigInteger(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('mention_type', sa.String(length=20), server_default='cashtag', nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['raw_content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_content_stock_mentions_content', 'content_stock_mentions', ['content_id'], unique=False)
    op.create_index('idx_content_stock_mentions_stock', 'content_stock_mentions', ['stock_id'], unique=False)
    op.create_index('idx_content_stock_mentions_unique', 'content_stock_mentions', ['content_id', 'stock_id'], unique=True)

    # Create sentiment_scores hypertable for time-series sentiment data
    op.create_table(
        'sentiment_scores',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'stock_id', 'source')
    )

    # Create mention_volumes hypertable for time-series mention counts
    op.create_table(
        'mention_volumes',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('baseline', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'stock_id', 'source')
    )

    # Create discoveries table
    op.create_table(
        'discoveries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('discovered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('volume_spike_magnitude', sa.Float(), nullable=True),
        sa.Column('sentiment_shift_magnitude', sa.Float(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('legitimacy_score', sa.Float(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('notified', sa.Boolean(), server_default='false', nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_discoveries_time', 'discoveries', ['discovered_at'], unique=False)
    op.create_index('idx_discoveries_stock', 'discoveries', ['stock_id'], unique=False)

    # Create watchlist table
    op.create_table(
        'watchlist',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('source', sa.String(length=50), server_default='manual', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id')
    )

    # Convert sentiment_scores and mention_volumes to TimescaleDB hypertables
    # This uses raw SQL since Alembic doesn't have native TimescaleDB support
    op.execute("SELECT create_hypertable('sentiment_scores', 'time', if_not_exists => TRUE)")
    op.execute("SELECT create_hypertable('mention_volumes', 'time', if_not_exists => TRUE)")

    # Create indexes on hypertables
    op.create_index('idx_sentiment_stock_time', 'sentiment_scores', ['stock_id', 'time'], unique=False)
    op.create_index('idx_mentions_stock_time', 'mention_volumes', ['stock_id', 'time'], unique=False)

    # Enable compression on hypertables (compress data older than 7 days)
    op.execute("""
        ALTER TABLE sentiment_scores SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'stock_id, source'
        )
    """)
    op.execute("""
        ALTER TABLE mention_volumes SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'stock_id, source'
        )
    """)
    op.execute("SELECT add_compression_policy('sentiment_scores', INTERVAL '7 days', if_not_exists => TRUE)")
    op.execute("SELECT add_compression_policy('mention_volumes', INTERVAL '7 days', if_not_exists => TRUE)")

    # Seed default scraped sources
    op.execute("""
        INSERT INTO scraped_sources (source_type, identifier, name, priority) VALUES
        ('reddit', 'wallstreetbets', 'WallStreetBets', 10),
        ('reddit', 'stocks', 'r/stocks', 8),
        ('reddit', 'investing', 'r/investing', 7),
        ('reddit', 'pennystocks', 'r/pennystocks', 6),
        ('reddit', 'stockmarket', 'r/stockmarket', 5)
    """)


def downgrade() -> None:
    # Remove compression policies first
    op.execute("SELECT remove_compression_policy('sentiment_scores', if_exists => TRUE)")
    op.execute("SELECT remove_compression_policy('mention_volumes', if_exists => TRUE)")

    # Drop tables in reverse order of creation
    op.drop_table('watchlist')
    op.drop_table('discoveries')
    op.drop_table('mention_volumes')
    op.drop_table('sentiment_scores')
    op.drop_index('idx_content_stock_mentions_unique', table_name='content_stock_mentions')
    op.drop_index('idx_content_stock_mentions_stock', table_name='content_stock_mentions')
    op.drop_index('idx_content_stock_mentions_content', table_name='content_stock_mentions')
    op.drop_table('content_stock_mentions')
    op.drop_index('idx_raw_content_unprocessed', table_name='raw_content')
    op.drop_index('idx_raw_content_source_id', table_name='raw_content')
    op.drop_index('idx_raw_content_source_collected', table_name='raw_content')
    op.drop_index('idx_raw_content_collected', table_name='raw_content')
    op.drop_table('raw_content')
    op.drop_index('idx_scraped_sources_type_id', table_name='scraped_sources')
    op.drop_index('idx_scraped_sources_active', table_name='scraped_sources')
    op.drop_table('scraped_sources')
    op.drop_index('idx_stocks_symbol', table_name='stocks')
    op.drop_table('stocks')
