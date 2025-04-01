# database.py
import os
import psycopg2
from contextlib import contextmanager
from psycopg2.extras import DictCursor

@contextmanager
def get_db():
    conn = psycopg2.connect(
        dsn=os.getenv("DATABASE_URL"),
        cursor_factory=DictCursor
    )
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL UNIQUE,
                    category VARCHAR(1) CHECK(category IN ('A', 'B')),
                    group_num TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    period TEXT NOT NULL,
                    internal_exam DATE,
                    state_exam DATE,
                    practical_exam DATE
                )
            ''')
            conn.commit()
