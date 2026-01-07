"""add news tables

Revision ID: add_news_tables
Revises: 060d5de49507
Create Date: 2026-01-07 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_news_tables'
down_revision = '060d5de49507'
branch_labels = None
depends_on = None


def upgrade():
    # Create news_articles table
    op.create_table(
        'news_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('symbols', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(length=20), nullable=True),
        sa.Column('sentiment_confidence', sa.Float(), nullable=True),
        sa.Column('sentiment_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_news_symbol_published', 'news_articles', ['published_at'], unique=False)
    op.create_index('idx_news_sentiment', 'news_articles', ['sentiment_label', 'sentiment_score'], unique=False)
    op.create_index(op.f('ix_news_articles_article_id'), 'news_articles', ['article_id'], unique=True)
    op.create_index(op.f('ix_news_articles_id'), 'news_articles', ['id'], unique=False)
    op.create_index(op.f('ix_news_articles_published_at'), 'news_articles', ['published_at'], unique=False)
    op.create_index(op.f('ix_news_articles_source'), 'news_articles', ['source'], unique=False)

    # Create sentiment_history table
    op.create_table(
        'sentiment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('avg_sentiment', sa.Float(), nullable=True),
        sa.Column('sentiment_std', sa.Float(), nullable=True),
        sa.Column('positive_count', sa.Integer(), nullable=True),
        sa.Column('neutral_count', sa.Integer(), nullable=True),
        sa.Column('negative_count', sa.Integer(), nullable=True),
        sa.Column('total_articles', sa.Integer(), nullable=True),
        sa.Column('weighted_sentiment', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sentiment_symbol_date', 'sentiment_history', ['symbol', 'date'], unique=False)
    op.create_index(op.f('ix_sentiment_history_date'), 'sentiment_history', ['date'], unique=False)
    op.create_index(op.f('ix_sentiment_history_id'), 'sentiment_history', ['id'], unique=False)
    op.create_index(op.f('ix_sentiment_history_symbol'), 'sentiment_history', ['symbol'], unique=False)


def downgrade():
    # Drop sentiment_history table
    op.drop_index(op.f('ix_sentiment_history_symbol'), table_name='sentiment_history')
    op.drop_index(op.f('ix_sentiment_history_id'), table_name='sentiment_history')
    op.drop_index(op.f('ix_sentiment_history_date'), table_name='sentiment_history')
    op.drop_index('idx_sentiment_symbol_date', table_name='sentiment_history')
    op.drop_table('sentiment_history')

    # Drop news_articles table
    op.drop_index(op.f('ix_news_articles_source'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_published_at'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_id'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_article_id'), table_name='news_articles')
    op.drop_index('idx_news_sentiment', table_name='news_articles')
    op.drop_index('idx_news_symbol_published', table_name='news_articles')
    op.drop_table('news_articles')
