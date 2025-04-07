from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)
    phone = Column(String)
    category = Column(String)
    group = Column(String)
    period = Column(String)
    theory_internal = Column(Date)
    theory_state = Column(Date)
    practice = Column(Date)
    address = Column(String)
