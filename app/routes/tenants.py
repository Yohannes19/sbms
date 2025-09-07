from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models import Tenant
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantRead
import app.services.tenants as svc
from app.routes.auth import require_user_ui

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("/ui")
def tenants_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenants = svc.list_tenants(db)
    return templates.TemplateResponse("tenants.html", {"request": request, "tenants": tenants, "current_user": current_user})

@router.get("/ui/new")
def tenant_new_ui(request: Request, current_user: User = Depends(require_user_ui)):
    # allow prefill via query params
    form = dict(request.query_params)
    return templates.TemplateResponse("tenant_form.html", {"request": request, "action": "create", "form": form, "current_user": current_user})

# server-side create
@router.post("/ui/new")
async def tenant_create_ui(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    form = await request.form()
    data = dict(form)

    # ensure is_active checkbox
    data["is_active"] = True if form.get("is_active") in ("on", "true", "1") else False

    # Accept metadata JSON from form field "metadata" but map to schema/model field metadata_json
    meta = form.get("metadata")
    if meta:
        try:
            import json
            data["metadata_json"] = json.loads(meta)
        except Exception:
            data["metadata_json"] = None

    try:
        payload = TenantCreate(**data)
    except Exception as e:
        return templates.TemplateResponse("tenant_form.html", {"request": request, "action": "create", "error": str(e), "form": data, "current_user": current_user}, status_code=400)

    tenant = svc.create_tenant(db, payload)
    return RedirectResponse(f"/tenants/ui/{tenant.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/ui/{tenant_id}")
def tenant_detail_ui(tenant_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    # provide a plain serializable dict for use by templates / JS
    tenant_data = TenantRead.from_orm(tenant).dict()
    return templates.TemplateResponse("tenant_detail.html", {"request": request, "tenant": tenant, "tenant_data": tenant_data, "current_user": current_user})

@router.get("/ui/{tenant_id}/edit")
def tenant_edit_ui(tenant_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant_data = TenantRead.from_orm(tenant).dict()
    return templates.TemplateResponse("tenant_form.html", {"request": request, "tenant": tenant, "tenant_data": tenant_data, "action": "edit", "current_user": current_user})

@router.post("/ui/{tenant_id}/edit")
async def tenant_edit_post(tenant_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    print("Tenant:", tenant)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    form = await request.form()
    data = dict(form)
    data["is_active"] = True if form.get("is_active") in ("on", "true", "1") else False

    meta = form.get("metadata")
    if meta:
        try:
            import json
            data["metadata_json"] = json.loads(meta)
        except Exception:
            data["metadata_json"] = None

    # build changes dict excluding empty strings
    changes = {k: v for k, v in data.items() if v not in (None, "")}
    try:
        updated = svc.update_tenant(db, tenant, **changes)
    except Exception as e:
        return templates.TemplateResponse("tenant_form.html", {"request": request, "tenant": tenant, "action": "edit", "error": str(e), "form": data, "current_user": current_user}, status_code=400)

    return RedirectResponse(f"/tenants/ui/{updated.id}", status_code=status.HTTP_303_SEE_OTHER)

# API endpoints
@router.get("/", response_model=List[TenantRead])
def list_tenants(db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    return svc.list_tenants(db)

@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    return svc.create_tenant(db, payload)

@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/{tenant_id}", response_model=TenantRead)
def update_tenant(tenant_id: int, payload: TenantUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    changes = payload.dict(exclude_unset=True)
    return svc.update_tenant(db, tenant, **changes)

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user_ui)):
    tenant = svc.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    svc.delete_tenant(db, tenant)
    return None