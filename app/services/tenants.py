from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Tenant
from app.schemas.tenant import TenantCreate

def list_tenants(db: Session) -> List[Tenant]:
    return db.query(Tenant).order_by(Tenant.id.desc()).all()

def get_tenant(db: Session, tenant_id: int) -> Optional[Tenant]:
    return db.get(Tenant, tenant_id)

def create_tenant(db: Session, payload: TenantCreate) -> Tenant:
    tenant = Tenant(**payload.dict())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

def update_tenant(db: Session, tenant: Tenant, **changes) -> Tenant:
    for k, v in changes.items():
        setattr(tenant, k, v)
    db.commit()
    db.refresh(tenant)
    return tenant

def delete_tenant(db: Session, tenant: Tenant) -> None:
    db.delete(tenant)
    db.commit()