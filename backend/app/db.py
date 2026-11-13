"""Data API: read-only access to the SQLite `dept` table."""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "company.db"

SCHEMA = """CREATE TABLE dept (
    id          TEXT PRIMARY KEY,   -- zero-padded code, e.g. '007'
    name        TEXT NOT NULL,
    description TEXT
);"""

MAX_ROWS = 200

_READ_ONLY = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)


class UnsafeSQLError(ValueError):
    pass


def run_query(sql: str) -> tuple[list[str], list[list]]:
    """Run a single read-only statement and return (columns, rows)."""
    sql = sql.strip().rstrip(";").strip()
    if not _READ_ONLY.match(sql) or ";" in sql:
        raise UnsafeSQLError("Only a single SELECT statement is allowed.")

    # mode=ro makes SQLite itself reject any write, as a second safeguard.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description or []]
        rows = [list(r) for r in cur.fetchmany(MAX_ROWS)]
        return columns, rows
    finally:
        conn.close()
