"""
Registration module - API для регистрации новых пользователей в системе.
"""
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, Request, status
from fastapi_limiter.depends import RateLimiter
from passlib.context import CryptContext
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_db
from app.models.users import Users
from app.schemas import CreateUser


router = APIRouter(prefix="/register", tags=["authentication"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    summary="Регистрация нового пользователя"
)
async def create_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    create_user: CreateUser,
) -> Dict[str, str]:
    """
    Регистрирует нового пользователя в системе.
    
    Хэширует пароль пользователя перед сохранением в базу данных.
    Ограничивает создание аккаунтов до 5 запросов в минуту.
    """
    await db.execute(
        insert(Users).values(
            email=create_user.email,
            password=bcrypt_context.hash(create_user.password),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}