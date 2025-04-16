import psycopg2
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from contextlib import contextmanager  # Добавлен импорт
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    @contextmanager  # Теперь декоратор определен
    def connect(self):
        """Контекстный менеджер для подключения к БД"""
        try:
            self.connection = psycopg2.connect(Config.DATABASE_URL)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            logger.info("Успешное подключение к базе данных")
            yield self.cursor
        except Exception as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            raise
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                logger.info("Соединение с базой данных закрыто")

    def create_tables(self):
        """Создание таблиц при первом запуске"""
        with self.connect() as cursor:  # Используем контекстный менеджер
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        fullname VARCHAR(200) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        category VARCHAR(5) NOT NULL,
                        group_num VARCHAR(50) NOT NULL,
                        period VARCHAR(50) NOT NULL,
                        exam_theory DATE,
                        exam_gos DATE,
                        exam_practice DATE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS requests (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(50) NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        question TEXT NOT NULL,
                        username VARCHAR(100),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                logger.info("Таблицы успешно созданы")
            except Exception as e:
                logger.error(f"Ошибка создания таблиц: {str(e)}")
                raise

db = Database()