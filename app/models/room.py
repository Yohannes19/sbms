from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False, index=True)
    floor = Column(String(50), nullable=True)
    capacity = Column(Integer, default=1)
    active = Column(Boolean, default=True)