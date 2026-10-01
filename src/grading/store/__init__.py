"""SQLite による保存。表の定義は schema.sql。"""

from grading.store.db import connect

__all__ = ["connect"]
