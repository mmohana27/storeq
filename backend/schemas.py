from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field , field_validator


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    stock: int


class SignupIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_password_rules(cls, v: str) -> str:  # R5.3
        if not 8 <= len(v) <= 20:
            raise ValueError("Password must be 8 to 20 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password needs an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password needs a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password needs a digit")
        return v


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=5)  # R2.2


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=5)  # R2.2


class CartLineOut(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    line_total: float


class CartOut(BaseModel):
    items: list[CartLineOut]
    total: float

class ReservationIn(BaseModel):
    store_id: int
    slot_start: datetime


class ReservationItemOut(BaseModel):
    product_id: int
    name: str
    quantity: int


class ReservationOut(BaseModel):
    id: int
    store_id: int
    slot_start: datetime
    status: str
    items: list[ReservationItemOut]


class SlotOut(BaseModel):
    slot_start: datetime
    available: bool
    remaining: int

class AppointmentIn(BaseModel):
    store_id: int
    slot_start: datetime


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    slot_start: datetime
    status: str

class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str