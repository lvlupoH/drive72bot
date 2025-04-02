from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    full_name = Column(String(100))
    group = Column(String(50))
    internal_exam = Column(Date)
    state_exam = Column(Date)
    practical_exam = Column(Date)
    exam_address = Column(String(200))
    notes = Column(String(500))

engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)