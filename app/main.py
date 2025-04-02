from fastapi import FastAPI
from app.auth import auth, register
from app.orders import order
from loguru import logger
from uuid import uuid4
from fastapi import FastAPI, Request
import time

from celery import Celery
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse




app = FastAPI()




app.include_router(auth.router)
app.include_router(register.router)
app.include_router(order.router)