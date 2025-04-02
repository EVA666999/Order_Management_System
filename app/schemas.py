from pydantic import BaseModel
from datetime import date


class CreateUser(BaseModel):
    email: str
    password: str

class CreateOrder(BaseModel):
    pass