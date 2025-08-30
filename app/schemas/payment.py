from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    contract_id: int
    amount: Decimal
    method: Optional[str] = None
    note: Optional[str] = None

class PaymentRead(PaymentCreate):
    id: int
    paid_at: datetime

    class Config:
        orm_mode = True