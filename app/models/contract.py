from datetime import date
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    rent_amount = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)

    tenant = relationship("Tenant", backref="contracts")
    room = relationship("Room", backref="contracts")