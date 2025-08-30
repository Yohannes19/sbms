from typing import List
from datetime import date
from sqlalchemy.orm import Session

from app.models import Contract, Tenant, Room
from app.schemas.contract import ContractCreate

def _overlaps(a_start: date, a_end: date | None, b_start: date, b_end: date | None) -> bool:
    # Treat None end as open-ended (infinite)
    a_end_eff = a_end or date.max
    b_end_eff = b_end or date.max
    return not (a_end_eff < b_start or b_end_eff < a_start)

def list_contracts(db: Session) -> List[Contract]:
    return db.query(Contract).order_by(Contract.id.desc()).all()

def get_contract(db: Session, contract_id: int) -> Contract | None:
    return db.get(Contract, contract_id)

def create_contract(db: Session, payload: ContractCreate) -> Contract:
    # verify tenant & room exist
    tenant = db.get(Tenant, payload.tenant_id)
    if not tenant:
        raise ValueError("Tenant not found")
    room = db.get(Room, payload.room_id)
    if not room:
        raise ValueError("Room not found")

    # check overlapping active contracts on the same room
    existing = db.query(Contract).filter(Contract.room_id == payload.room_id, Contract.active == True).all()
    for c in existing:
        if _overlaps(payload.start_date, payload.end_date, c.start_date, c.end_date):
            raise ValueError(f"Contract overlaps with existing active contract id={c.id}")

    contract = Contract(**payload.dict())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract

def update_contract(db: Session, contract: Contract, **changes) -> Contract:
    for k, v in changes.items():
        setattr(contract, k, v)
    db.commit()
    db.refresh(contract)
    return contract

def delete_contract(db: Session, contract: Contract) -> None:
    db.delete(contract)
    db.commit()