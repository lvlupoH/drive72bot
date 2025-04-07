from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    full_name = Column(String(100))
    phone = Column(String(20))
    category = Column(String(20))
    group = Column(String(50))
    period = Column(String(50))
    theory_internal = Column(Date)
    theory_state = Column(Date)
    practice = Column(Date)
    address = Column(String(200))