from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date
from decimal import Decimal

class ContractBase(BaseModel):
    tenant_id: int
    room_id: int
    start_date: date
    end_date: Optional[date] = None
    rent_amount: Decimal

    @field_validator("rent_amount")
    def rent_must_be_positive(cls, v: Decimal):
        if v is None or v <= 0:
            raise ValueError("rent_amount must be greater than 0")
        return v

    @model_validator(mode="before")
    def validate_dates(cls, values: dict):
        start = values.get("start_date")
        end = values.get("end_date")
        if start and end and end < start:
            raise ValueError("end_date must be the same or after start_date")
        return values

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[Decimal] = None
    active: Optional[bool] = None

    @model_validator(mode="before")
    def validate_dates(cls, values: dict):
        start = values.get("start_date")
        end = values.get("end_date")
        if start and end and end < start:
            raise ValueError("end_date must be the same or after start_date")
        return values

class ContractRead(ContractBase):
    id: int
    active: bool

    class Config:
        orm_mode = True