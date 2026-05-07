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

# ─── Schemas de Request para entidades auxiliares ────────────────────────────────────────

class CreateCustomerRequest(BaseModel):
    firstName: str = Field(..., examples=["Juan"])
    lastName: str = Field(..., examples=["Perez"])
    city: str = Field(..., examples=["Buenos Aires"])
    country: str = Field(..., examples=["Argentina"])
    phone: str = Field(..., examples=["+5491122334455"])

class UpdateCustomerRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None

class CreateProductRequest(BaseModel):
    productName: str = Field(..., examples=["Laptop"])
    unitPrice: float = Field(..., examples=[1500.0])
    package: str = Field(..., examples=["Standard"])
    isDiscontinued: bool = Field(False)
    supplierId: Optional[int] = None

class UpdateProductRequest(BaseModel):
    productName: Optional[str] = None
    unitPrice: Optional[float] = None
    package: Optional[str] = None
    isDiscontinued: Optional[bool] = None
    supplierId: Optional[int] = None

class CreateSupplierRequest(BaseModel):
    companyName: str = Field(..., examples=["Tech Corp"])
    contactName: str = Field(..., examples=["Ana"])
    contactTitle: str = Field(..., examples=["Manager"])
    city: str = Field(..., examples=["Madrid"])
    country: str = Field(..., examples=["Spain"])
    phone: str = Field(..., examples=["+34911223344"])
    fax: Optional[str] = None

class UpdateSupplierRequest(BaseModel):
    companyName: Optional[str] = None
    contactName: Optional[str] = None
    contactTitle: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None

# ─── Modelo de respuesta paginada genérica (usada por varios recursos) ────────────────────────
class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list

# Alias específicos para claridad
class OrderListResponse(PaginatedResponse):
    items: list[Order]

class ProductListResponse(PaginatedResponse):
    items: list[Product]

class CustomerListResponse(PaginatedResponse):
    items: list[Customer]

class SupplierListResponse(PaginatedResponse):
    items: list[Supplier]
