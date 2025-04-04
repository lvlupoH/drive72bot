from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

engine = create_engine(Config.DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(String(50), unique=True)
    fullname = Column(String(100))
    group = Column(String(50))
    internal_exam = Column(String(20))
    state_exam = Column(String(20))
    practical_exam = Column(String(20))
    address = Column(String(200))

Base.metadata.create_all(engine)
