from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

class RoomBase(BaseModel):
    number: str
    floor: Optional[str] = None
    capacity: Optional[int] = 1
    active: Optional[bool] = True

    # new fields
    title: Optional[str] = None
    description: Optional[str] = None
    bed_count: Optional[int] = None
    max_occupancy: Optional[int] = None
    sq_meters: Optional[float] = None
    price: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None

    has_ac: Optional[bool] = False
    private_bath: Optional[bool] = False
    accessible: Optional[bool] = False

    amenities: Optional[List[Any]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None

    available: Optional[bool] = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    number: Optional[str] = None
    floor: Optional[str] = None
    capacity: Optional[int] = None
    active: Optional[bool] = None

    title: Optional[str] = None
    description: Optional[str] = None
    bed_count: Optional[int] = None
    max_occupancy: Optional[int] = None
    sq_meters: Optional[float] = None
    price: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None

    has_ac: Optional[bool] = None
    private_bath: Optional[bool] = None
    accessible: Optional[bool] = None

    amenities: Optional[List[Any]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None

    available: Optional[bool] = None

class RoomRead(RoomBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True