from decimal import Decimal
from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.routes.auth import require_user_ui

from app.db.session import get_db
from app.models import Contract, Tenant, Room, Payment
from app.schemas import ContractCreate, ContractRead, ContractUpdate, tenant
import app.services.contracts as svc
import app.services.payments as payments_svc

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/contracts", tags=["contracts"])

# -- HTML UI endpoints (register these first so "/ui" is matched before "/{contract_id}") --
@router.get("/ui")
def contracts_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contracts = svc.list_contracts(db)
    return templates.TemplateResponse(
        "contracts.html", 
        {"request": request, "contracts": contracts, "current_user": current_user}
    )

@router.get("/ui/new")
def contract_new_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    rooms = db.query(Room).order_by(Room.id.desc()).all()
    return templates.TemplateResponse(
        "contract_form.html", 
        {"request": request, "tenants": tenants, "rooms": rooms, "action": "create", "current_user": current_user}
    )

@router.get("/ui/{contract_id}")
def contract_detail_ui(contract_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    payments = db.query(Payment).filter(Payment.contract_id == contract.id).order_by(Payment.paid_at.desc()).all()
    total_paid = payments_svc.total_paid_for_contract(db, contract.id)
    return templates.TemplateResponse(
        "contract_detail.html", 
        {"request": request, "contract": contract, "payments": payments, "total_paid": total_paid, "current_user": current_user}
    )

@router.get("/ui/{contract_id}/edit")
def contract_edit_ui(contract_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    rooms = db.query(Room).order_by(Room.id.desc()).all()
    return templates.TemplateResponse(
        "contract_form.html", 
        {"request": request, "contract": contract, "tenants": tenants, "rooms": rooms, "action": "edit", "current_user": current_user}
    )

@router.post("/ui/new")
async def contract_create_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    form = await request.form()
    print("form:", form)
    data = dict(form)
    print("data:", data)

    try:
        payload = ContractCreate(**data)
    except Exception as e:
        return templates.TemplateResponse("contract_form.html", {"request": request, "action": "create", "error": str(e), "form": data, "current_user": current_user}, status_code=400)

    contract = svc.create_contract(db, payload)
    return RedirectResponse(f"/contracts/ui/{contract.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/ui/{contract_id}/edit")
async def contract_edit_post(contract_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contract = svc.get_contract(db, contract_id)
    print("Contract:", contract)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    form = await request.form()
    data = dict(form)


    # build changes dict excluding empty strings
    changes = {k: v for k, v in data.items() if v not in (None, "")}
    try:
        updated = svc.update_contract(db, contract, **changes)
    except Exception as e:
        return templates.TemplateResponse("contract_form.html", {"request": request, "contract": contract, "action": "edit", "error": str(e), "form": data, "current_user": current_user}, status_code=400)

    return RedirectResponse(f"/contracts/ui/{updated.id}", status_code=status.HTTP_303_SEE_OTHER)

# -- JSON API endpoints --
@router.get("/", response_model=List[ContractRead])
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    return svc.list_contracts(db)

@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    try:
        return svc.create_contract(db, payload)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
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
def delete_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    contract = svc.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    svc.delete_contract(db, contract)
    return None