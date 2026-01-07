"""add news alerts

Revision ID: add_news_alerts
Revises: add_news_tables
Create Date: 2026-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_news_alerts'
down_revision = 'add_news_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum values to alertcondition (uppercase to match existing pattern)
    op.execute("ALTER TYPE alertcondition ADD VALUE IF NOT EXISTS 'SENTIMENT_ABOVE'")
    op.execute("ALTER TYPE alertcondition ADD VALUE IF NOT EXISTS 'SENTIMENT_BELOW'")
    op.execute("ALTER TYPE alertcondition ADD VALUE IF NOT EXISTS 'SENTIMENT_CHANGE'")
    op.execute("ALTER TYPE alertcondition ADD VALUE IF NOT EXISTS 'NEWS_VOLUME_SPIKE'")

    # Add new columns to alert_history table
    op.alter_column('alert_history', 'price_at_trigger',
                    existing_type=sa.Float(),
                    nullable=True)

    op.add_column('alert_history', sa.Column('sentiment_at_trigger', sa.Float(), nullable=True))
    op.add_column('alert_history', sa.Column('articles_count', sa.Integer(), nullable=True))
    op.add_column('alert_history', sa.Column('trigger_details', sa.String(1000), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('alert_history', 'trigger_details')
    op.drop_column('alert_history', 'articles_count')
    op.drop_column('alert_history', 'sentiment_at_trigger')

    op.alter_column('alert_history', 'price_at_trigger',
                    existing_type=sa.Float(),
                    nullable=False)

    # Note: PostgreSQL doesn't support removing enum values easily
    # so we leave them in the enum type
