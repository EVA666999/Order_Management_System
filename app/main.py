from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth, register
from app.orders import order
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await FastAPILimiter.init(redis_client)

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(order.router)
