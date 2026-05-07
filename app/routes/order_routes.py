"""
Definición de rutas / endpoints de la API.
En FastAPI los routers combinan la función de routes + controllers de Express.
"""

from fastapi import APIRouter, HTTPException, Response, status

from app.models.schemas import (
    Order,
    Product,
    OrderItem,
    Customer,
    Supplier,
    CreateOrderRequest,
    ReplaceOrderRequest,
    PatchOrderRequest,
    AddItemRequest,
    UpdateItemQuantityRequest,
    OrderListResponse,
    ProductListResponse,
    CustomerListResponse,
    SupplierListResponse,
    CreateCustomerRequest,
    UpdateCustomerRequest,
    CreateProductRequest,
    UpdateProductRequest,
    CreateSupplierRequest,
    UpdateSupplierRequest,
)
from typing import Optional
from fastapi import Query
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

# ─── Inyección de dependencias ────────────────────────────────────
order_repository = OrderRepository()
order_service = OrderService(order_repository)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
#  ORDERS
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/orders",
    response_model=OrderListResponse,
    summary="Pedidos",
    description="lista pedidos.",
)
def get_all_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    customerId: Optional[int] = Query(None, description="Filter by customer ID"),
    dateFrom: Optional[str] = Query(None, description="Filter by start date"),
    dateTo: Optional[str] = Query(None, description="Filter by end date"),
    sort: Optional[str] = Query(None, description="Field to sort by (prefix with '-' for descending)")
):
    return order_service.get_orders_paginated(page, limit, customerId, dateFrom, dateTo, sort)


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    summary="Detalle PEDIDO",
    responses={404: {"description": "No encontrado."}},
)
def get_order_by_id(order_id: int):
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un pedido",
    description="Crea pedido. totalAmount se calcula automáticamente.",
    responses={400: {"description": "Error de validación  cliente o producto no existe."}},
)
def create_order(body: CreateOrderRequest):
    items_data = [item.model_dump() for item in body.items]
    return order_service.create_order(body.customerId, items_data)


@router.put(
    "/orders/{order_id}",
    response_model=Order,
    summary="Reemplazar  pedido",
    responses={
        400: {"description": "Error validación."},
        404: {"description": "Pedido no encontrado."},
    },
)
def replace_order(order_id: int, body: ReplaceOrderRequest):
    items_data = [item.model_dump() for item in body.items]
    result = order_service.replace_order(order_id, body.customerId, items_data)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.patch(
    "/orders/{order_id}",
    response_model=Order,
    summary="Actualizar pedido",
    responses={404: {"description": "No encontrado."}},
)
def patch_order(order_id: int, body: PatchOrderRequest):
    result = order_service.patch_order(order_id, body.customerId, body.orderDate)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar  pedido",
    responses={404: {"description": "Pedido no encontrado."}},
)
def delete_order(order_id: int):
    deleted = order_service.delete_order(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════
#  ORDER ITEMS
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/orders/{order_id}/items",
    response_model=list[OrderItem],
    summary="items pedido",
    responses={404: {"description": "Pedido no encontrado."}},
)
def get_order_items(order_id: int):
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.items


@router.post(
    "/orders/{order_id}/items",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar  producto a  pedido",
    responses={404: {"description": "Pedido no encontrado."}},
)
def add_product_to_order(order_id: int, body: AddItemRequest):
    result = order_service.add_product_to_order(order_id, body.productId, body.quantity)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.patch(
    "/orders/{order_id}/items/{item_id}",
    response_model=Order,
    summary="Actualizar cantidad de  item",
    responses={404: {"description": "Pedido no encontrado."}},
)
def update_item_quantity(order_id: int, item_id: int, body: UpdateItemQuantityRequest):
    result = order_service.update_item_quantity(order_id, item_id, body.quantity)
    if not result:
        raise HTTPException(status_code=404, detail="Order  not found")
    return result


@router.delete(
    "/orders/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar  item del pedido",
    responses={404: {"description": "Pedido no encontrado."}},
)
def remove_item(order_id: int, item_id: int):
    result = order_service.remove_item_from_order(order_id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════
#  PRODUCTS
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="Lista productos",
)
def get_all_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    supplierId: Optional[int] = Query(None, description="Filter by supplier ID"),
    search: Optional[str] = Query(None, description="Search by product name"),
    discontinued: Optional[bool] = Query(None, description="Filter by discontinued status"),
    sort: Optional[str] = Query(None, description="Field to sort by (prefix with '-' for descending)")
):
    return order_service.get_products_paginated(page, limit, supplierId, search, discontinued, sort)


@router.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Detalle  producto",
    responses={404: {"description": "Producto no encontrado."}},
)
def get_product_by_id(product_id: int):
    product = order_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def create_product(body: CreateProductRequest):
    return order_service.create_product(body.model_dump())

@router.put(
    "/products/{product_id}",
    response_model=Product,
    summary="Reemplazar producto",
)
def replace_product(product_id: int, body: CreateProductRequest):
    result = order_service.replace_product(product_id, body.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@router.patch(
    "/products/{product_id}",
    response_model=Product,
    summary="Actualizar parcialmente producto",
)
def patch_product(product_id: int, body: UpdateProductRequest):
    result = order_service.update_product(product_id, body.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto",
)
def delete_product(product_id: int):
    if not order_service.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found or conflict")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ─── Customers ────────────────────────────────────────────────

@router.get(
    "/customers",
    response_model=CustomerListResponse,
    summary="Lista clientes",
)
def get_all_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort: Optional[str] = Query(None, description="Field to sort by (prefix with '-' for descending)")
):
    return order_service.get_customers_paginated(page, limit, country, city, search, sort)

@router.get(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Detalle cliente",
    responses={404: {"description": "Cliente no encontrado."}},
)
def get_customer_by_id(customer_id: int):
    customer = order_service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get(
    "/customers/{customer_id}/orders",
    response_model=list[Order],
    summary="Pedidos del cliente",
    responses={404: {"description": "Cliente no encontrado."}},
)
def get_orders_by_customer(customer_id: int):
    # Verify customer exists
    customer = order_service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return order_service.get_orders_by_customer(customer_id)

@router.post(
    "/customers",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente",
)
def create_customer(body: CreateCustomerRequest):
    return order_service.create_customer(body.model_dump())

@router.patch(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Actualizar parcialmente un cliente",
)
def patch_customer(customer_id: int, body: UpdateCustomerRequest):
    result = order_service.update_customer(customer_id, body.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result

# ─── Suppliers ────────────────────────────────────────────────

@router.get(
    "/suppliers",
    response_model=SupplierListResponse,
    summary="Lista proveedores",
)
def get_all_suppliers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search by company name"),
    sort: Optional[str] = Query(None, description="Field to sort by (prefix with '-' for descending)")
):
    return order_service.get_suppliers_paginated(page, limit, country, city, search, sort)

@router.get(
    "/suppliers/{supplier_id}",
    response_model=Supplier,
    summary="Detalle proveedor",
    responses={404: {"description": "Proveedor no encontrado."}},
)
def get_supplier_by_id(supplier_id: int):
    supplier = order_service.get_supplier_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.get(
    "/suppliers/{supplier_id}/products",
    response_model=list[Product],
    summary="Productos del proveedor",
    responses={404: {"description": "Proveedor no encontrado."}},
)
def get_products_by_supplier(supplier_id: int):
    supplier = order_service.get_supplier_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return order_service.get_products_by_supplier(supplier_id)

@router.post(
    "/suppliers",
    response_model=Supplier,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proveedor",
)
def create_supplier(body: CreateSupplierRequest):
    return order_service.create_supplier(body.model_dump())

@router.patch(
    "/suppliers/{supplier_id}",
    response_model=Supplier,
    summary="Actualizar parcialmente proveedor",
)
def patch_supplier(supplier_id: int, body: UpdateSupplierRequest):
    result = order_service.update_supplier(supplier_id, body.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return result

