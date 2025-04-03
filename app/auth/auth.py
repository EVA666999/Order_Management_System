"""
Authentication module - API для аутентификации и JWT токенов.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_db
from app.models.users import Users

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
ALGORITHM = "HS256"

router = APIRouter(prefix="/token", tags=["authentication"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(db: AsyncSession, email: str, password: str):
   """Аутентифицирует пользователя по email и паролю"""
   user = await db.scalar(select(Users).where(Users.email == email))
   if not user or not bcrypt_context.verify(password, user.password):
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Invalid authentication credentials",
           headers={"WWW-Authenticate": "Bearer"},
       )
   return user


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
   """Создает JWT токен доступа"""
   to_encode = data.copy()
   expire = datetime.now(timezone.utc) + expires_delta
   to_encode.update({"exp": expire})
   return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
   """Извлекает пользователя из JWT токена"""
   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       email = payload.get("sub")
       user_id = payload.get("id")
       if email is None or user_id is None:
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
       return {"email": email, "id": user_id}
   except jwt.PyJWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post(
   "/",
   status_code=status.HTTP_200_OK,
   dependencies=[Depends(RateLimiter(times=5, seconds=60))],
   summary="Получение JWT токена"
)
async def login_for_access_token(
   request: Request,
   form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
   db: Annotated[AsyncSession, Depends(get_db)],
):
   """Аутентифицирует пользователя и создает JWT токен"""
   user = await authenticate_user(db, form_data.username, form_data.password)
   if not user:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

   access_token = create_access_token(data={"sub": user.email, "id": user.id})
   return {"access_token": access_token, "token_type": "bearer"}


@router.get(
   "/me",
   status_code=status.HTTP_200_OK,
   dependencies=[Depends(RateLimiter(times=5, seconds=60))],
   summary="Получение данных пользователя"
)
async def read_users_me(
   request: Request, current_user: Annotated[dict, Depends(get_current_user)]
):
   """Возвращает данные текущего пользователя"""
   return current_user