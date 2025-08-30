from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Contract, Tenant, Room, Payment
from app.schemas import ContractCreate, ContractRead, ContractUpdate
import app.services.contracts as svc
import app.services.payments as payments_svc

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/contracts", tags=["contracts"])

# -- HTML UI endpoints (register these first so "/ui" is matched before "/{contract_id}") --
@router.get("/ui")
def contracts_ui(request: Request, db: Session = Depends(get_db)):
    contracts = svc.list_contracts(db)
    return templates.TemplateResponse("contracts.html", {"request": request, "contracts": contracts})

@router.get("/ui/new")
def contract_new_ui(request: Request, db: Session = Depends(get_db)):
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    rooms = db.query(Room).order_by(Room.id.desc()).all()
    return templates.TemplateResponse("contract_form.html", {"request": request, "tenants": tenants, "rooms": rooms, "action": "create"})

@router.get("/ui/{contract_id}")
def contract_detail_ui(contract_id: int, request: Request, db: Session = Depends(get_db)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # payments for this contract and total paid
    payments = db.query(Payment).filter(Payment.contract_id == contract.id).order_by(Payment.paid_at.desc()).all()
    total_paid = payments_svc.total_paid_for_contract(db, contract.id)

    return templates.TemplateResponse(
        "contract_detail.html",
        {"request": request, "contract": contract, "payments": payments, "total_paid": total_paid}
    )

@router.get("/ui/{contract_id}/edit")
def contract_edit_ui(contract_id: int, request: Request, db: Session = Depends(get_db)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    rooms = db.query(Room).order_by(Room.id.desc()).all()
    return templates.TemplateResponse("contract_form.html", {"request": request, "contract": contract, "tenants": tenants, "rooms": rooms, "action": "edit"})

# -- JSON API endpoints --
@router.get("/", response_model=List[ContractRead])
def list_contracts(db: Session = Depends(get_db)):
    return svc.list_contracts(db)

@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    try:
        return svc.create_contract(db, payload)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    changes = payload.dict(exclude_unset=True)
    try:
        updated = svc.update_contract(db, contract, **changes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    svc.delete_contract(db, contract)
    return None