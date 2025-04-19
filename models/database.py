import psycopg2
from utils.config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        
    def connect(self):
        try:
            self.conn = psycopg2.connect(Config.DATABASE_URL)
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            raise

    def get_all_students(self):
        try:
            self.connect()
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM students")
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            return []
        finally:
            if self.conn:
                self.conn.close()

    def add_student(self, student_data: dict):
        try:
            self.connect()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO students 
                    (username, fullname, phone, category, group_num, 
                    period, exam_theory, exam_gos, exam_practice)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    student_data['username'],
                    student_data['fullname'],
                    student_data['phone'],
                    student_data['category'],
                    student_data['group_num'],
                    student_data['period'],
                    student_data['exam_theory'],
                    student_data['exam_gos'],
                    student_data['exam_practice']
                ))
                self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            self.conn.rollback()
        finally:
            if self.conn:
                self.conn.close()
                
    def search_student(self, search_term: str):
        query = """
             SELECT * FROM students 
             WHERE fullname ILIKE %s OR phone ILIKE %s
        """
        return self.execute_query(query, (f"%{search_term}%", f"%{search_term}%"), fetch=True)

    def delete_student_by_name_and_phone(self, fullname: str, phone: str):
        query = "DELETE FROM students WHERE fullname = %s AND phone = %s"
        self.execute_query(query, (fullname, phone))

    def delete_student(self, username: str):
        try:
            self.connect()
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM students WHERE username = %s", (username,))
                self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            self.conn.rollback()
        finally:
            if self.conn:
                self.conn.close()

# Создаем экземпляр базы данных
db = Database()