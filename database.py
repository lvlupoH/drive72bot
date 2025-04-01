import os
import psycopg2
from contextlib import contextmanager
from psycopg2.extras import DictCursor
from typing import Generator

@contextmanager
def get_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """Контекстный менеджер для подключения к базе данных"""
    conn = psycopg2.connect(
        dsn=os.getenv("DATABASE_URL"),
        cursor_factory=DictCursor
    )
    try:
        yield conn
    except psycopg2.DatabaseError as e:
        print(f"Database error: {str(e)}")
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Инициализация базы данных и создание таблиц"""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Создание таблицы пользователей
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL UNIQUE,
                    category VARCHAR(1) CHECK (category IN ('A', 'B')),
                    group_num VARCHAR(20) NOT NULL,
                    full_name TEXT NOT NULL,
                    period VARCHAR(21) NOT NULL,
                    internal_exam DATE,
                    state_exam DATE,
                    practical_exam DATE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Создание индекса для быстрого поиска по user_id
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_user_id 
                ON users (user_id)
            ''')
            
        conn.commit()
