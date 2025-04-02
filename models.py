# models.py
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    full_name = Column(String)
    group = Column(String)
    internal_exam = Column(Date)
    state_exam = Column(Date)
    practical_exam = Column(Date)
    exam_address = Column(String)
    notes = Column(String)

# Инициализация базы данных
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)