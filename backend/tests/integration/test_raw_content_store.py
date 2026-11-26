"""Needs Postgres with `alembic upgrade head` applied; skips otherwise."""
import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.db import engine
from app.models.sentiment import RawContent
from app.services.raw_content_store import save_raw_content


@pytest.fixture
def db():
    try:
        conn = engine.connect()
        conn.execute(text("SELECT 1 FROM raw_content LIMIT 1"))
    except Exception as e:
        pytest.skip(f"database or raw_content table not available: {e}")
    conn.rollback()  # end the transaction the probe query started
    trans = conn.begin()
    session = Session(bind=conn)
    yield session
    session.close()
    trans.rollback()
    conn.close()


def test_same_item_saved_once(db):
    row = dict(source="reddit", source_id="t3_dedupe_test", content="hello")
    assert save_raw_content(db, **row) is True
    assert save_raw_content(db, **row) is False
    count = db.scalar(
        select(func.count()).select_from(RawContent).where(RawContent.source_id == "t3_dedupe_test")
    )
    assert count == 1
