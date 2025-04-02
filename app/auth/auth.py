from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
import jwt

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

import os

from app.models.users import User
from app.schemas import CreateUser
from app.database.db_depends import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


ALGORITHM = 'HS256'

router = APIRouter(prefix='/register', tags=['register'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.post('/')
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    await db.execute(insert(User).values(email=create_user.email,
                                         password=bcrypt_context.hash(create_user.password),
                                         ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }
