from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, func
from sqlalchemy.types import JSON
from app.db.session import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # new detailed fields
    dob = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    street = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)

    id_type = Column(String(50), nullable=True)
    id_number = Column(String(100), nullable=True)
    photo = Column(String(500), nullable=True)

    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)

    move_in_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)  # DB column stays "metadata", attribute is metadata_json
    is_active = Column(Boolean, default=True)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)