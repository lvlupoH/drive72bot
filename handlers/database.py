import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn_params = {
            'dsn': Config.DATABASE_URL,
            'isolation_level': ISOLATION_LEVEL_AUTOCOMMIT
        }

    @contextmanager
    def get_cursor(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.conn_params)
            with conn.cursor() as cursor:
                yield cursor
            conn.commit()
        except Exception as e:
            logger.error(f"DB Error: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        with self.get_cursor() as cur:
            try:
                # Students table
                cur.execute("""
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
                
                # Requests table
                cur.execute("""
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
                logger.info("Tables created successfully")
            except Exception as e:
                logger.error(f"Table creation failed: {str(e)}")
                raise

# Initialize database
db = Database()
db.create_tables()