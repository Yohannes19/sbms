import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import Tenant, Room
from app.services.contracts import create_contract
from app.schemas.contract import ContractCreate
from decimal import Decimal
from datetime import date

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

def test_create_and_detect_overlap(session):
    # prepare tenant and room
    t = Tenant(name="Alice")
    r = Room(number="101")
    session.add_all([t, r])
    session.commit()
    session.refresh(t)
    session.refresh(r)

    payload1 = ContractCreate(
        tenant_id=t.id,
        room_id=r.id,
        start_date=date(2025,1,1),
        end_date=date(2025,12,31),
        rent_amount=Decimal("1000.00")
    )
    c1 = create_contract(session, payload1)
    assert c1.id is not None

    # overlapping contract (should raise)
    payload_overlap = ContractCreate(
        tenant_id=t.id,
        room_id=r.id,
        start_date=date(2025,6,1),
        end_date=date(2026,1,1),
        rent_amount=Decimal("1100.00")
    )
    with pytest.raises(ValueError):
        create_contract(session, payload_overlap)

    # non-overlapping in future should succeed
    payload2 = ContractCreate(
        tenant_id=t.id,
        room_id=r.id,
        start_date=date(2026,1,2),
        end_date=date(2026,12,31),
        rent_amount=Decimal("1200.00")
    )
    c2 = create_contract(session, payload2)
    assert c2.id is not None