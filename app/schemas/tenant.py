from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict
from datetime import date, datetime

class TenantBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    dob: Optional[date] = None
    gender: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

    id_type: Optional[str] = None
    id_number: Optional[str] = None
    photo: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    move_in_date: Optional[date] = None
    notes: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    photo: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    move_in_date: Optional[date] = None
    notes: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TenantRead(TenantBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True