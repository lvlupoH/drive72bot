from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CallbackRequest(Base):
    __tablename__ = 'callback_requests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    question = Column(Text, nullable=False)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)