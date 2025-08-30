import os
import sys

# ensure project root is on sys.path so "import app" works when running the script directly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from decimal import Decimal
from datetime import date, datetime
from typing import Optional

from app.db.session import SessionLocal, engine, Base
from app.models import Tenant, Room, Contract, Payment

# Optional: create tables if you didn't run migrations (safe in dev)
# Base.metadata.create_all(bind=engine)

def get_or_create(session, model, lookup: dict, defaults: Optional[dict] = None):
    obj = session.query(model).filter_by(**lookup).first()
    if obj:
        return obj, False
    data = {**lookup}
    if defaults:
        data.update(defaults)
    obj = model(**data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj, True

def seed():
    session = SessionLocal()
    try:
        print("Seeding tenants...")
        t1, created = get_or_create(session, Tenant, {"email": "alice@example.com"}, {"name": "Alice", "phone": "555-0101"})
        t2, created = get_or_create(session, Tenant, {"email": "bob@example.com"}, {"name": "Bob", "phone": "555-0202"})

        print("Seeding rooms...")
        r1, _ = get_or_create(session, Room, {"number": "101"}, {"floor": "1", "capacity": 1, "active": True})
        r2, _ = get_or_create(session, Room, {"number": "102"}, {"floor": "1", "capacity": 2, "active": True})
        r3, _ = get_or_create(session, Room, {"number": "201"}, {"floor": "2", "capacity": 1, "active": True})

        print("Seeding contracts...")
        # create one active contract for Alice in room 101
        existing = session.query(Contract).filter(Contract.tenant_id == t1.id, Contract.room_id == r1.id).first()
        if not existing:
            c1 = Contract(
                tenant_id=t1.id,
                room_id=r1.id,
                start_date=date(2025, 1, 1),
                end_date=None,
                rent_amount=Decimal("800.00"),
                active=True
            )
            session.add(c1)
            session.commit()
            session.refresh(c1)
        else:
            c1 = existing

        # create a historical contract for Bob in room 201
        existing = session.query(Contract).filter(Contract.tenant_id == t2.id, Contract.room_id == r3.id).first()
        if not existing:
            c2 = Contract(
                tenant_id=t2.id,
                room_id=r3.id,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                rent_amount=Decimal("600.00"),
                active=False
            )
            session.add(c2)
            session.commit()
            session.refresh(c2)
        else:
            c2 = existing

        print("Seeding payments...")
        # Add one payment for c1
        p_exists = session.query(Payment).filter(Payment.contract_id == c1.id, Payment.amount == Decimal("800.00")).first()
        if not p_exists:
            p1 = Payment(contract_id=c1.id, amount=Decimal("800.00"), paid_at=datetime.utcnow(), method="bank", note="January rent")
            session.add(p1)
            session.commit()
            session.refresh(p1)

        # Add a payment for c2
        p_exists = session.query(Payment).filter(Payment.contract_id == c2.id).first()
        if not p_exists:
            p2 = Payment(contract_id=c2.id, amount=Decimal("600.00"), paid_at=datetime(2024,1,5), method="cash", note="Jan rent")
            session.add(p2)
            session.commit()
            session.refresh(p2)

        print("Seeding complete.")
        print(f"Tenant IDs: {t1.id}, {t2.id}")
        print(f"Room IDs: {r1.id}, {r2.id}, {r3.id}")
        print(f"Contracts: {c1.id}, {c2.id}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()