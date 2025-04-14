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

    def execute_query(self, query, params=None, fetch=False):
        """Универсальный метод для выполнения запросов"""
        try:
            self.connect()
            self.cursor.execute(query, params)
            
            if fetch:
                result = self.cursor.fetchall()
                return result
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {str(e)}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()

    # ------------------- CRUD операции для студентов -------------------
    def add_student(self, student_data):
        """Добавление нового студента"""
        query = sql.SQL("""
            INSERT INTO students 
            (username, fullname, phone, category, group_num, period, 
            exam_theory, exam_gos, exam_practice)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        self.execute_query(query, tuple(student_data.values()))

    def delete_student(self, username):
        """Удаление студента по username"""
        query = "DELETE FROM students WHERE username = %s"
        self.execute_query(query, (username,))

    def get_student(self, username):
        """Получение данных студента"""
        query = "SELECT * FROM students WHERE username = %s"
        return self.execute_query(query, (username,), fetch=True)

    # ------------------- Работа с запросами -------------------
    def add_request(self, request_data):
        """Добавление запроса (обратный звонок/доп. занятия)"""
        query = """
            INSERT INTO requests 
            (type, name, phone, question, username)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_query(query, (
            request_data['type'],
            request_data['name'],
            request_data['phone'],
            request_data['question'],
            request_data.get('username')
        ))

    def get_all_requests(self):
        """Получение всех запросов"""
        query = "SELECT * FROM requests ORDER BY created_at DESC"
        return self.execute_query(query, fetch=True)

# Инициализация базы данных при импорте
db = Database()
db.create_tables()