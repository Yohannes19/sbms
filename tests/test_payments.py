import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import date

from app.db.session import Base
from app.models import Tenant, Room, Contract
from app.services.payments import create_payment, total_paid_for_contract
from app.schemas.payment import PaymentCreate

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_payment_and_total(session):
    t = Tenant(name="Bob")
    r = Room(number="201")
    session.add_all([t, r])
    session.commit()
    session.refresh(t); session.refresh(r)

    c = Contract(tenant_id=t.id, room_id=r.id, start_date=date(2025,1,1), end_date=None, rent_amount=Decimal("500.00"))
    session.add(c)
    session.commit()
    session.refresh(c)

    payload = PaymentCreate(contract_id=c.id, amount=Decimal("500.00"), method="bank", note="Rent")
    p = create_payment(session, payload)
    assert p.id is not None

    total = total_paid_for_contract(session, c.id)
    assert total == Decimal("500.00")