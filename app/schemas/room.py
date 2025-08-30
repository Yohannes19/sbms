from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    number: str
    floor: Optional[str] = None
    capacity: Optional[int] = 1
    active: Optional[bool] = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    number: Optional[str] = None
    floor: Optional[str] = None
    capacity: Optional[int] = None
    active: Optional[bool] = None

class RoomRead(RoomBase):
    id: int

    class Config:
        orm_mode = True