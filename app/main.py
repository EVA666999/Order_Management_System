from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth, register
from app.orders import order

app = FastAPI()

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

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(order.router)
