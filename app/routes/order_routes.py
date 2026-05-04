"""
Definición de rutas / endpoints de la API.
En FastAPI los routers combinan la función de routes + controllers de Express.
"""

from fastapi import APIRouter, HTTPException, Response, status

from app.models.schemas import (
    Order,
    Product,
    OrderItem,
    CreateOrderRequest,
    ReplaceOrderRequest,
    PatchOrderRequest,
    AddItemRequest,
    UpdateItemQuantityRequest,
)
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
    response_model=list[Order],
    summary="Listar pedidos",
    description="Retorna una lista de todos los pedidos.",
)
def get_all_orders():
    return order_service.get_all_orders()


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    summary="Obtener detalle de un pedido",
    responses={404: {"description": "Pedido no encontrado."}},
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
    description="Crea un nuevo pedido. El totalAmount se calcula automáticamente.",
    responses={400: {"description": "Error de validación (ej. cliente o producto no existe)."}},
)
def create_order(body: CreateOrderRequest):
    items_data = [item.model_dump() for item in body.items]
    return order_service.create_order(body.customerId, items_data)


@router.put(
    "/orders/{order_id}",
    response_model=Order,
    summary="Reemplazar completamente un pedido",
    responses={
        400: {"description": "Error de validación."},
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
    summary="Actualizar parcialmente un pedido",
    responses={404: {"description": "Pedido no encontrado."}},
)
def patch_order(order_id: int, body: PatchOrderRequest):
    result = order_service.patch_order(order_id, body.customerId, body.orderDate)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o anular un pedido",
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
    summary="Listar items de un pedido",
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
    summary="Agregar un producto a un pedido existente",
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
    summary="Actualizar cantidad de un item",
    responses={404: {"description": "Pedido o item no encontrado."}},
)
def update_item_quantity(order_id: int, item_id: int, body: UpdateItemQuantityRequest):
    result = order_service.update_item_quantity(order_id, item_id, body.quantity)
    if not result:
        raise HTTPException(status_code=404, detail="Order or item not found")
    return result


@router.delete(
    "/orders/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un item del pedido",
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
    response_model=list[Product],
    summary="Listar productos",
)
def get_all_products():
    return order_service.get_all_products()


@router.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Detalle de un producto",
    responses={404: {"description": "Producto no encontrado."}},
)
def get_product_by_id(product_id: int):
    product = order_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
