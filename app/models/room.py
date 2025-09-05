from sqlalchemy import Column, Integer, String, Boolean, Float, Numeric, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSON
from app.db.session import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False, index=True)
    floor = Column(String(50), nullable=True)
    capacity = Column(Integer, default=1)
    active = Column(Boolean, default=True)

    # new fields
    title = Column(String(200), nullable=True)               # human-friendly title
    description = Column(Text, nullable=True)
    bed_count = Column(Integer, nullable=True)
    max_occupancy = Column(Integer, nullable=True)
    sq_meters = Column(Float, nullable=True)
    price = Column(Numeric(10,2), nullable=True)
    deposit_amount = Column(Numeric(10,2), nullable=True)

    has_ac = Column(Boolean, default=False)
    private_bath = Column(Boolean, default=False)
    accessible = Column(Boolean, default=False)

    amenities = Column(JSON, nullable=True)   # list/dict of amenities
    tags = Column(JSON, nullable=True)        # list of tags
    images = Column(JSON, nullable=True)      # list of image URLs

    available = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)