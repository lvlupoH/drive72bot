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

# Инициализация движка БД
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """Модель пользователя (ученика)"""
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
    password_hash = Column(String(60))  # Для входа в ЛК

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

class CallbackRequest(Base):
    """Модель запросов обратного звонка"""
    __tablename__ = 'callbacks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    request_type = Column(String(20))  # 'callback' или 'extra_lesson'
    question = Column(Text)
    created_at = Column(Date, default=datetime.now)
    
    user = relationship("User")

class Instructor(Base):
    """Модель инструкторов"""
    __tablename__ = 'instructors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    photo_url = Column(String(200))  # CDN URL
    description = Column(Text)
    car_model = Column(String(50))

# Утилиты работы с БД
def get_db():
    """Генератор сессий БД"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
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
                question=data['question'],
                created_at=datetime.now()
            )
            session.add(new_callback)
            session.commit()
            logger.info(f"New callback saved: {new_callback.id}")
    except Exception as e:
        logger.error(f"Error saving callback: {str(e)}")
        raise

def create_student(data: dict):
    """Добавление нового ученика"""
    try:
        with SessionLocal() as session:
            student = User(
                username=data['username'],
                full_name=data['full_name'],
                phone=data['phone'],
                category=data['category'],
                group=data.get('group'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                theory_exam=data.get('theory_exam'),
                state_exam=data.get('state_exam'),
                practice_exam=data.get('practice_exam')
            )
            if 'password' in data:
                student.set_password(data['password'])
            session.add(student)
            session.commit()
            logger.info(f"New student created: {student.username}")
            return student
    except SQLAlchemyError as e:
        logger.error(f"Error creating student: {str(e)}")
        raise

def get_student_profile(username: str):
    """Получение данных для ЛК ученика"""
    try:
        with SessionLocal() as session:
            return session.query(User).filter_by(username=username).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching student: {str(e)}")
        return None

# Инициализация БД (для Alembic)
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
