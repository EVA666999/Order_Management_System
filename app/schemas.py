from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any


class CreateUser(BaseModel):
    email: str
    password: str


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class CreateOrder(BaseModel):
    items: List[Dict[str, Any]]
    total_price: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = datetime.utcnow()


class UpdateStatus(BaseModel):
    status: OrderStatus = OrderStatus.PENDING
