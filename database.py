from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from config import Config
import logging
from datetime import datetime
import bcrypt

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    category = Column(String(20), nullable=False)
    group = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    theory_exam = Column(Date)
    state_exam = Column(Date)
    practice_exam = Column(Date)
    password_hash = Column(String(60))

    # Отношения
    callbacks = relationship("CallbackRequest", back_populates="user")
    extra_lessons = relationship("ExtraLesson", back_populates="user")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

class CallbackRequest(Base):
    """Модель запросов обратного звонка"""
    __tablename__ = 'callbacks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    request_type = Column(String(20))  # 'callback' или 'extra'
    question = Column(Text)
    created_at = Column(Date, default=datetime.now)
    
    user = relationship("User", back_populates="callbacks")

class ExtraLesson(Base):
    """Модель дополнительных занятий"""
    __tablename__ = 'extra_lessons'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    schedule = Column(Text)
    created_at = Column(Date, default=datetime.now)
    
    user = relationship("User", back_populates="extra_lessons")

def get_db():
    """Генератор сессий БД"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Ошибка БД: {str(e)}")
        db.rollback()
    finally:
        db.close()

def save_callback(data: dict):
    """Сохранение запроса обратного звонка"""
    try:
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=data['username']).first()
            new_callback = CallbackRequest(
                user_id=user.id,
                request_type=data['type'],
                question=data['question']
            )
            session.add(new_callback)
            session.commit()
            logger.info(f"Новый запрос сохранён: {new_callback.id}")
    except Exception as e:
        logger.error(f"Ошибка сохранения запроса: {str(e)}")
        raise

def save_extra(data: dict):
    """Сохранение данных о доп. занятиях"""
    try:
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=data['username']).first()
            new_extra = ExtraLesson(
                user_id=user.id,
                schedule=data['schedule']
            )
            session.add(new_extra)
            session.commit()
            logger.info(f"Новое занятие сохранено: {new_extra.id}")
    except Exception as e:
        logger.error(f"Ошибка сохранения занятия: {str(e)}")
        raise

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы БД успешно созданы")