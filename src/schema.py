
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add repo root to path
from DbConnector import DbConnector   # uses your .env values

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"

def run_sql_file(cursor, sql_text: str):
    """
    Execute multiple SQL statements in one go.
    Uses mysql-connector's multi=True.
    """
    for _ in cursor.execute(sql_text, multi=True):
        pass

def main():
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Missing {SCHEMA_FILE}")
    sql_text = SCHEMA_FILE.read_text(encoding="utf-8")

    db = DbConnector()
    try:
        cursor = db.cursor
        print(f"Applying schema from {SCHEMA_FILE} …")
        run_sql_file(cursor, sql_text)
        db.db_connection.commit()
        print("Schema applied.")
        # quick sanity check
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables:", ", ".join(tables))
    finally:
        try:
            db.close_connection()
        except Exception:
            pass

if __name__ == "__main__":
    main()
