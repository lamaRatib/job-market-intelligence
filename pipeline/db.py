import sqlite3
import os

DB_PATH = os.path.join("data", "processed", "jobs.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_jobs (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    source                  TEXT NOT NULL,
    source_tier             TEXT NOT NULL,  -- 'global' | 'palestine' | 'remote'
    external_id             TEXT,
    title                   TEXT,
    company                 TEXT,
    location                TEXT,
    country_code            TEXT,
    is_remote               INTEGER DEFAULT 0,  -- 0/1 boolean
    skills                  TEXT,               -- comma-separated
    job_category            TEXT,
    date_posted             TEXT,
    url                     TEXT,
    is_palestine_mentioned  INTEGER DEFAULT 0,
    hash                    TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_counts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    skill       TEXT NOT NULL,
    source_tier TEXT NOT NULL,
    count       INTEGER DEFAULT 0,
    UNIQUE(skill, source_tier)
);
"""

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()