import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import Tenant
from app.services.tenants import create_tenant, get_tenant, list_tenants, update_tenant, delete_tenant
from app.schemas.tenant import TenantCreate

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

def test_crud_tenant(session):
    payload = TenantCreate(name="Charlie", email="charlie@example.com", phone="1234")
    t = create_tenant(session, payload)
    assert t.id is not None
    assert t.name == "Charlie"

    t2 = get_tenant(session, t.id)
    assert t2.email == "charlie@example.com"

    all_t = list_tenants(session)
    assert len(all_t) == 1

    updated = update_tenant(session, t, name="Charles")
    assert updated.name == "Charles"

    delete_tenant(session, updated)
    assert get_tenant(session, t.id) is None