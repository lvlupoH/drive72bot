import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = psycopg2.connect(Config.DATABASE_URL)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            raise

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            logger.info("Соединение с базой данных закрыто")

    def create_tables(self):
        """Создание таблиц при первом запуске"""
        try:
            self.connect()
            
            # Таблица студентов
            self.cursor.execute("""
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
            
            # Таблица запросов
            self.cursor.execute("""
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
        finally:
            self.disconnect()

db = Database()