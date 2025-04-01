# database.py
import sqlite3
from contextlib import contextmanager
from config import Config
import logging

logger = logging.getLogger(__name__)

DATABASE_NAME = Config.DATABASE_URL  # Из конфига

@contextmanager
def get_db():
    """Контекстный менеджер для работы с базой данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Доступ к колонкам по имени
    try:
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Инициализация таблиц в базе данных"""
    with get_db() as conn:
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    category TEXT CHECK(category IN ('A', 'B')) NOT NULL,
                    group_num TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    period TEXT NOT NULL,
                    internal_exam TEXT,
                    state_exam TEXT,
                    practical_exam TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Init DB error: {str(e)}")
            raise

def add_user(user_data: dict):
    """Добавление пользователя в базу данных"""
    with get_db() as conn:
        try:
            conn.execute('''
                INSERT INTO users (
                    user_id, category, group_num,
                    full_name, period, internal_exam,
                    state_exam, practical_exam
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'],
                user_data['category'],
                user_data['group_num'],
                user_data['full_name'],
                user_data['period'],
                user_data.get('internal_exam'),
                user_data.get('state_exam'),
                user_data.get('practical_exam')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning("User already exists")
            return False
        except Exception as e:
            logger.error(f"Add user error: {str(e)}")
            return False

def get_user(user_id: int):
    """Получение данных пользователя"""
    with get_db() as conn:
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None

def update_user(user_id: int, update_data: dict):
    """Обновление данных пользователя"""
    with get_db() as conn:
        try:
            set_clause = ", ".join([f"{k}=?" for k in update_data.keys()])
            values = list(update_data.values()) + [user_id]
            
            conn.execute(
                f"UPDATE users SET {set_clause} WHERE user_id = ?",
                values
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Update user error: {str(e)}")
            return False
