from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Payment, Contract
from app.models.user import User
from app.routes.auth import require_user_ui
from app.schemas import PaymentCreate, PaymentRead
import app.services.payments as svc

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/payments", tags=["payments"])

# UI endpoints (register before param routes)
@router.get("/ui")
def payments_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    payments = svc.list_payments(db)
    contracts = db.query(Contract).order_by(Contract.id.desc()).all()
    return templates.TemplateResponse("payments.html", {"request": request, "payments": payments, "current_user": current_user, "contracts": contracts})

@router.get("/ui/new")
def payment_new_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contracts = db.query(Contract).order_by(Contract.id.desc()).all()
    return templates.TemplateResponse("payment_form.html", {"request": request, "contracts": contracts, "action": "create", "current_user": current_user})

@router.get("/ui/{payment_id}")
def payment_detail_ui(payment_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    payment = svc.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return templates.TemplateResponse("payment_detail.html", {"request": request, "payment": payment, "current_user": current_user})

# API endpoints
@router.get("/", response_model=List[PaymentRead])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    return svc.list_payments(db)

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    try:
        return svc.create_payment(db, payload)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    payment = svc.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    payment = svc.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    svc.delete_payment(db, payment)
    return None