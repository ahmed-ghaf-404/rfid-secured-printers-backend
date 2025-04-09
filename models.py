from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base

def oman_now():
    return datetime.utcnow() + timedelta(hours=4)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    rfid_uid = Column(String, unique=True, index=True)
    name = Column(String)

    print_jobs = relationship("PrintJob", back_populates="user")

class PrintJob(Base):
    __tablename__ = "print_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="printed")
    timestamp = Column(DateTime, default=oman_now)

    user = relationship("User", back_populates="print_jobs")
