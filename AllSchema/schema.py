from pydantic import BaseModel
from typing import Optional

class CustomerSchema(BaseModel):
    name: str
    email: str
    address: Optional[str]
    password: str
    phone_number: str

    class Config:
        orm_mode = True

class ManufacturerSchema(BaseModel):
    name: str
    email: str
    address: Optional[str]
    password: str
    phone_number: str

    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    name: str
    description: str
    stock: int
    MRP: int
    costPrice: int
    Discount: Optional[int]

    class Config:
        orm_mode = True

class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    phone_number: str
    address: str

    class Config:
        orm_mode = True


class ManufacturerResponse(BaseModel):
    manufacturer_id: int
    name: str
    email: str
    phone_number: str
    address: str

    class Config:
        orm_mode = True


class ManufacturerLogin(BaseModel):
    manufacturer_id: int
    password: str

class CustomerLogin(BaseModel):
    customer_id: int
    password: str