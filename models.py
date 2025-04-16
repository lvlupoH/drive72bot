from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CallbackRequest(Base):
class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    fullname = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    category = Column(String(5), nullable=False)
    group_num = Column(String(50), nullable=False)
    period = Column(String(50), nullable=False)
    exam_theory = Column(Date)
    exam_gos = Column(Date)
    exam_practice = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

class Request(Base):
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    question = Column(Text, nullable=False)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    