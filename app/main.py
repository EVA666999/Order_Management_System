from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth, register
from app.orders import order

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from .rate_limiter import limiter

app = FastAPI()
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):

    logger.warning(f"Rate limit exceeded for IP: {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later.",
            "client_ip": request.client.host
        }
    )


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
