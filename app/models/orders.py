import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from enum import Enum as PyEnum


class OrderStatus(PyEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    items: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
