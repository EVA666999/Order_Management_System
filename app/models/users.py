from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer


from app.database.db import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)

    orders = relationship("Orders", back_populates="user")
