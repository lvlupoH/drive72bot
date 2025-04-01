import os
import psycopg2
from contextlib import contextmanager
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError

@contextmanager
def get_db():
    """Контекстный менеджер для подключения к базе данных"""
    conn = None
    try:
        conn = psycopg2.connect(
            dsn=os.getenv("DATABASE_URL"),
            cursor_factory=DictCursor,
            sslmode='require' if os.getenv('ENV') == 'production' else None
        )
        conn.autocommit = True
        yield conn
    except OperationalError as e:
        print(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Инициализация структуры базы данных"""
    with get_db() as conn:
        with conn.cursor() as cur:
            try:
                # Таблица пользователей
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

                # Таблица запросов
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS requests (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(20) NOT NULL,
                        full_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Индексы для оптимизации
                cur.execute('''
                    CREATE INDEX IF NOT EXISTS idx_users_user_id 
                    ON users (user_id)
                ''')

                print("✅ Database initialized successfully")
                
            except Exception as e:
                print(f"❌ Database initialization error: {str(e)}")
                raise
