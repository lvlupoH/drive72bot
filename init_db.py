import psycopg2
from config import Config

def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS requests (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50),
            name VARCHAR(100),
            phone VARCHAR(20),
            question TEXT,
            username VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        )
        """,
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
            exam_practice DATE
        );
    )
    
    conn = None
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
        print("Таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_tables()
