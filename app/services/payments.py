from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Payment, Contract
from app.schemas.payment import PaymentCreate

def list_payments(db: Session) -> List[Payment]:
    return db.query(Payment).order_by(Payment.paid_at.desc()).all()

def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    return db.get(Payment, payment_id)

def create_payment(db: Session, payload: PaymentCreate) -> Payment:
    contract = db.get(Contract, payload.contract_id)
    if not contract:
        raise ValueError("Contract not found")
    if payload.amount is None or payload.amount <= Decimal("0"):
        raise ValueError("amount must be greater than 0")
    payment = Payment(**payload.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def delete_payment(db: Session, payment: Payment) -> None:
    db.delete(payment)
    db.commit()

def total_paid_for_contract(db: Session, contract_id: int) -> Decimal:
    total = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.contract_id == contract_id).scalar()
    return Decimal(total)