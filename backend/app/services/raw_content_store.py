"""Race-safe insert for RawContent."""
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.sentiment import RawContent


def save_raw_content(db: Session, **values) -> bool:
    """Insert one row. Return False if (source, source_id) is already stored.

    Relies on the unique index idx_raw_content_source_id, so two overlapping
    runs cannot both insert the same item.
    """
    stmt = (
        insert(RawContent)
        .values(**values)
        .on_conflict_do_nothing(index_elements=['source', 'source_id'])
    )
    return db.execute(stmt).rowcount == 1
