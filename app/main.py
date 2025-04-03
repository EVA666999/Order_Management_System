from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth, register
from app.orders import order
from loguru import logger
from fastapi.responses import JSONResponse
from uuid import uuid4
import time

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from celery import Celery
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from .rate_limiter import limiter

app = FastAPI()

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "detail": f"Rate limit exceeded. Try again in {exc.retry_after} seconds."
        }
    )

# Настройка CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(order.router)