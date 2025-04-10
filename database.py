from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import Config
import logging
from datetime import datetime
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    full_name = Column(String(100))
    phone = Column(String(20))
    category = Column(String(20))
    group = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    theory_exam = Column(Date)
    state_exam = Column(Date)
    practice_exam = Column(Date)
    password_hash = Column(String(60))

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

class CallbackRequest(Base):
    __tablename__ = 'callbacks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    request_type = Column(String(20))
    question = Column(Text)
    created_at = Column(Date, default=datetime.now)
    user = relationship("User")

class ExtraLesson(Base):
    __tablename__ = 'extra_lessons'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    schedule = Column(Text)
    created_at = Column(Date, default=datetime.now)
    user = relationship("User")

def save_callback(data: dict):
    try:
        with SessionLocal() as session:
            callback = CallbackRequest(
                user_id=data['user_id'],
                request_type=data['type'],
                question=data['question']
            )
            session.add(callback)
            session.commit()
            logger.info(f"Callback saved: {callback.id}")
    except Exception as e:
        logger.error(f"Error saving callback: {str(e)}")
        raise

def save_extra(data: dict):
    try:
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=data['username']).first()
            extra = ExtraLesson(
                user_id=user.id,
                schedule=data['schedule']
            )
            session.add(extra)
            session.commit()
            logger.info(f"Extra lesson saved: {extra.id}")
    except Exception as e:
        logger.error(f"Error saving extra: {str(e)}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")