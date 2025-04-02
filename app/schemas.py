from pydantic import BaseModel
from datetime import date


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int

class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None

class CreateUser(BaseModel):
    email: str
    password: str

class CreateReview(BaseModel):
    user_id: int
    product_id: int
    comment: str
    comment_date: date
    rating: int
    is_active: bool = True