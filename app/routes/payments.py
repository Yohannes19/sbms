from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Payment, Contract
from app.schemas import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[PaymentRead])
def list_payments(db: Session = Depends(get_db)):
    return db.query(Payment).order_by(Payment.paid_at.desc()).all()

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    contract = db.get(Contract, payload.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    payment = Payment(**payload.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(payment)
    db.commit()
    return None