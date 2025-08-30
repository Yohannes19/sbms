from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    amount = Column(Numeric(10,2), nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    method = Column(String(50), nullable=True)
    note = Column(String(500), nullable=True)

    contract = relationship("Contract", backref="payments")