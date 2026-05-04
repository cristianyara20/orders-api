"""
Modelos Pydantic para la API de Órdenes.
Equivalente a los interfaces TypeScript del proyecto original.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─── Entidades base ───────────────────────────────────────────────

class Supplier(BaseModel):
    id: int
    companyName: str
    contactName: str
    contactTitle: str
    city: str
    country: str
    phone: str
    fax: Optional[str] = None


class Product(BaseModel):
    id: int
    productName: str
    unitPrice: float
    package: str
    isDiscontinued: bool
    supplier: Optional[Supplier] = None


class Customer(BaseModel):
    id: int
    firstName: str
    lastName: str
    city: str
    country: str
    phone: str


class OrderItem(BaseModel):
    id: int
    product: Product
    unitPrice: float
    quantity: int


class Order(BaseModel):
    id: int
    orderNumber: str
    orderDate: str
    totalAmount: float
    customer: Customer
    items: list[OrderItem]


# ─── Schemas de Request ──────────────────────────────────────────

class CreateOrderItemRequest(BaseModel):
    productId: int = Field(..., examples=[1])
    quantity: int = Field(..., gt=0, examples=[2])


class CreateOrderRequest(BaseModel):
    customerId: int = Field(..., examples=[1])
    items: list[CreateOrderItemRequest]


class ReplaceOrderRequest(BaseModel):
    customerId: int = Field(..., examples=[2])
    items: list[CreateOrderItemRequest]


class PatchOrderRequest(BaseModel):
    customerId: Optional[int] = Field(None, examples=[2])
    orderDate: Optional[str] = Field(None, examples=["2026-05-01T10:00:00Z"])


class AddItemRequest(BaseModel):
    productId: int = Field(..., examples=[3])
    quantity: int = Field(..., gt=0, examples=[5])


class UpdateItemQuantityRequest(BaseModel):
    quantity: int = Field(..., gt=0, examples=[10])
