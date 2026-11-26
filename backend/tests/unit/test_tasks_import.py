"""Catches import errors in app.tasks and beat entries that name a missing task."""
import app.tasks  # noqa: F401  (a NameError/ImportError here fails the test)
from app.celery_app import celery_app


def test_every_beat_task_is_registered():
    registered = set(celery_app.tasks)
    missing = [
        name for name, entry in celery_app.conf.beat_schedule.items()
        if entry["task"] not in registered
    ]
    assert not missing, f"beat entries point at unregistered tasks: {missing}"
