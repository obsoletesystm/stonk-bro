"""unique (source, source_id) on raw_content

Revision ID: 20260126000000
Revises: 20260122095405
Create Date: 2026-01-26 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20260126000000'
down_revision = '20260122095405'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep the oldest row of any duplicate before the index becomes unique.
    op.execute("""
        DELETE FROM raw_content a USING raw_content b
        WHERE a.source = b.source AND a.source_id = b.source_id AND a.id > b.id
    """)
    op.drop_index('idx_raw_content_source_id', table_name='raw_content')
    op.create_index('idx_raw_content_source_id', 'raw_content', ['source', 'source_id'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_raw_content_source_id', table_name='raw_content')
    op.create_index('idx_raw_content_source_id', 'raw_content', ['source', 'source_id'], unique=False)
