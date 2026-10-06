import sqlite3
from importlib.resources import files
from pathlib import Path


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    """DB に接続し、表が無ければ作る。"""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(files("grading.store").joinpath("schema.sql").read_text(encoding="utf-8"))
    return conn
