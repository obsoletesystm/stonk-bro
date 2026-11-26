"""seed default RSS feeds

Revision ID: 20260122095405
Revises: 20260121224647
Create Date: 2026-01-22 09:54:05.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260122095405'
down_revision = '20260121224647'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Seed default RSS feeds for financial news.

    These feeds cover major financial news sources that focus on stock market coverage.
    """
    # Default RSS feeds for stock-related news
    default_feeds = [
        # Major financial news
        {
            'name': 'Reuters Business News',
            'identifier': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
            'source_type': 'news',
            'is_active': True
        },
        {
            'name': 'Yahoo Finance - Stock Market News',
            'identifier': 'https://finance.yahoo.com/news/rssindex',
            'source_type': 'news',
            'is_active': True
        },
        {
            'name': 'MarketWatch - Top Stories',
            'identifier': 'http://feeds.marketwatch.com/marketwatch/topstories/',
            'source_type': 'news',
            'is_active': True
        },
        {
            'name': 'Seeking Alpha - Market News',
            'identifier': 'https://seekingalpha.com/market_currents.xml',
            'source_type': 'news',
            'is_active': True
        },
        {
            'name': 'Benzinga - All',
            'identifier': 'https://www.benzinga.com/feed',
            'source_type': 'news',
            'is_active': True
        },
        # Canadian sources (for TFSA focus)
        {
            'name': 'Globe and Mail - Business',
            'identifier': 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/',
            'source_type': 'news',
            'is_active': True
        },
        {
            'name': 'Financial Post',
            'identifier': 'https://financialpost.com/feed/',
            'source_type': 'news',
            'is_active': True
        },
    ]

    # Insert feeds
    op.execute(
        sa.text("""
            INSERT INTO scraped_sources (name, source_type, identifier, is_active, created_at, updated_at)
            VALUES
                ('Reuters Business News', 'news', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best', true, NOW(), NOW()),
                ('Yahoo Finance - Stock Market News', 'news', 'https://finance.yahoo.com/news/rssindex', true, NOW(), NOW()),
                ('MarketWatch - Top Stories', 'news', 'http://feeds.marketwatch.com/marketwatch/topstories/', true, NOW(), NOW()),
                ('Seeking Alpha - Market News', 'news', 'https://seekingalpha.com/market_currents.xml', true, NOW(), NOW()),
                ('Benzinga - All', 'news', 'https://www.benzinga.com/feed', true, NOW(), NOW()),
                ('Globe and Mail - Business', 'news', 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/', true, NOW(), NOW()),
                ('Financial Post', 'news', 'https://financialpost.com/feed/', true, NOW(), NOW())
            ON CONFLICT (identifier) DO NOTHING;
        """)
    )


def downgrade() -> None:
    """
    Remove default RSS feeds.
    """
    op.execute(
        sa.text("""
            DELETE FROM scraped_sources
            WHERE source_type = 'news'
            AND identifier IN (
                'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
                'https://finance.yahoo.com/news/rssindex',
                'http://feeds.marketwatch.com/marketwatch/topstories/',
                'https://seekingalpha.com/market_currents.xml',
                'https://www.benzinga.com/feed',
                'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/',
                'https://financialpost.com/feed/'
            );
        """)
    )
