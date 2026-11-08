"""Registry for GDPR export/deletion.

Each team registers two functions that take a user_id:
  exporter(user_id) -> JSON-serialisable data about that user
  deleter(user_id)  -> delete or anonymise that user's data in their area
Our endpoints call every registered function. We cannot know other teams'
tables, but they can.

Example (Team 1 would write this in their code):
    from app.gdpr_hooks import register
    register("reservations", exporter=my_export, deleter=my_delete)
"""
from typing import Any, Callable

EXPORTERS: dict[str, Callable[[int], Any]] = {}
DELETERS: dict[str, Callable[[int], None]] = {}


def register(name: str, exporter: Callable[[int], Any],
             deleter: Callable[[int], None]) -> None:
    EXPORTERS[name] = exporter
    DELETERS[name] = deleter
