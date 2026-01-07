"""Change is_tfsa to boolean

Revision ID: 060d5de49507
Revises: 5765ca62c81f
Create Date: 2026-01-07 05:00:53.753030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '060d5de49507'
down_revision = '5765ca62c81f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert is_tfsa from INTEGER to BOOLEAN with USING clause
    op.execute('ALTER TABLE portfolios ALTER COLUMN is_tfsa TYPE BOOLEAN USING (is_tfsa::boolean)')


def downgrade() -> None:
    # Convert is_tfsa back from BOOLEAN to INTEGER
    op.execute('ALTER TABLE portfolios ALTER COLUMN is_tfsa TYPE INTEGER USING (is_tfsa::integer)')
