from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Tenant
from app.schemas import TenantCreate, TenantRead, TenantUpdate
import app.services.tenants as svc

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/tenants", tags=["tenants"])

# UI endpoints (register before param routes)
@router.get("/ui")
def tenants_ui(request: Request, db: Session = Depends(get_db)):
    tenants = svc.list_tenants(db)
    return templates.TemplateResponse("tenants.html", {"request": request, "tenants": tenants})

@router.get("/ui/new")
def tenant_new_ui(request: Request):
    return templates.TemplateResponse("tenant_form.html", {"request": request, "action": "create"})

@router.get("/ui/{tenant_id}")
def tenant_detail_ui(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return templates.TemplateResponse("tenant_detail.html", {"request": request, "tenant": tenant})

@router.get("/ui/{tenant_id}/edit")
def tenant_edit_ui(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return templates.TemplateResponse("tenant_form.html", {"request": request, "tenant": tenant, "action": "edit"})

# API endpoints
@router.get("/", response_model=List[TenantRead])
def list_tenants(db: Session = Depends(get_db)):
    return svc.list_tenants(db)

@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    return svc.create_tenant(db, payload)

@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/{tenant_id}", response_model=TenantRead)
def update_tenant(tenant_id: int, payload: TenantUpdate, db: Session = Depends(get_db)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    changes = payload.dict(exclude_unset=True)
    return svc.update_tenant(db, tenant, **changes)

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    svc.delete_tenant(db, tenant)
    return None