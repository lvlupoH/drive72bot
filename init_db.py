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
