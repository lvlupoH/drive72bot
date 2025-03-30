# database.py
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    lessons_left = Column(Integer)

# Инициализация подключения к БД
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

async def get_user_data(telegram_id: int):
    """Получение данных пользователя из БД"""
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            return {
                "start_date": user.start_date.strftime("%Y-%m-%d"),
                "end_date": user.end_date.strftime("%Y-%m-%d"),
                "lessons_left": user.lessons_left
            }
        return None
    finally:
        session.close()

# Добавьте в конец database.py
def init_test_data():
    session = Session()
    try:
        if not session.query(User).first():
            test_user = User(
                telegram_id=249423404,  # Ваш Telegram ID
                start_date="2025-01-01",
                end_date="2025-12-31",
                lessons_left=10
            )
            session.add(test_user)
            session.commit()
    finally:
        session.close()

# Вызов функции при первом запуске
init_test_data()
