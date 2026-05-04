"""
Capa de lógica de negocio – Equivalente al OrderService de TypeScript.
Contiene las validaciones y el cálculo automático de totalAmount.
"""

import random
import time
from typing import Optional

from fastapi import HTTPException, status

from app.models.schemas import Order, OrderItem, Product, Customer
from app.repositories.order_repository import OrderRepository


class OrderService:
    """Lógica de negocio para órdenes, items y productos."""

    def __init__(self, repository: OrderRepository) -> None:
        self.repo = repository

    # ─── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _calculate_total(items: list[OrderItem]) -> float:
        return sum(item.unitPrice * item.quantity for item in items)

    @staticmethod
    def _generate_id() -> int:
        return random.randint(1, 99999)

    # ─── Orders ───────────────────────────────────────────────────

    def get_all_orders(self) -> list[Order]:
        return self.repo.find_all_orders()

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.repo.find_order_by_id(order_id)

    def create_order(
        self, customer_id: int, items_data: list[dict]
    ) -> Order:
        # Validar cliente
        customers = self.repo.find_all_customers()
        customer = next((c for c in customers if c.id == customer_id), None)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with ID {customer_id} not found",
            )

        # Construir items
        items: list[OrderItem] = []
        for item_data in items_data:
            product = self.repo.find_product_by_id(item_data["productId"])
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {item_data['productId']} not found",
                )
            items.append(
                OrderItem(
                    id=self._generate_id(),
                    product=product,
                    unitPrice=product.unitPrice,
                    quantity=item_data["quantity"],
                )
            )

        new_order = Order(
            id=self._generate_id(),
            orderNumber=f"ORD-{int(time.time() * 1000)}",
            orderDate=time.strftime("%Y-%m-%dT%H:%M:%S"),
            totalAmount=self._calculate_total(items),
            customer=customer,
            items=items,
        )

        return self.repo.save_order(new_order)

    def replace_order(
        self, order_id: int, customer_id: int, items_data: list[dict]
    ) -> Optional[Order]:
        existing = self.repo.find_order_by_id(order_id)
        if not existing:
            return None

        customers = self.repo.find_all_customers()
        customer = next((c for c in customers if c.id == customer_id), None)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with ID {customer_id} not found",
            )

        items: list[OrderItem] = []
        for item_data in items_data:
            product = self.repo.find_product_by_id(item_data["productId"])
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {item_data['productId']} not found",
                )
            items.append(
                OrderItem(
                    id=self._generate_id(),
                    product=product,
                    unitPrice=product.unitPrice,
                    quantity=item_data["quantity"],
                )
            )

        replaced = existing.model_copy(
            update={
                "customer": customer,
                "items": items,
                "totalAmount": self._calculate_total(items),
            }
        )
        return self.repo.update_order(order_id, replaced)

    def patch_order(
        self, order_id: int, customer_id: Optional[int], order_date: Optional[str]
    ) -> Optional[Order]:
        existing = self.repo.find_order_by_id(order_id)
        if not existing:
            return None

        updates: dict = {}

        if customer_id is not None:
            customers = self.repo.find_all_customers()
            new_customer = next((c for c in customers if c.id == customer_id), None)
            if new_customer:
                updates["customer"] = new_customer

        if order_date is not None:
            updates["orderDate"] = order_date

        if updates:
            patched = existing.model_copy(update=updates)
            return self.repo.update_order(order_id, patched)

        return existing

    def delete_order(self, order_id: int) -> bool:
        return self.repo.delete_order(order_id)

    # ─── Order Items ──────────────────────────────────────────────

    def add_product_to_order(
        self, order_id: int, product_id: int, quantity: int
    ) -> Optional[Order]:
        order = self.repo.find_order_by_id(order_id)
        if not order:
            return None

        product = self.repo.find_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {product_id} not found",
            )

        new_item = OrderItem(
            id=self._generate_id(),
            product=product,
            unitPrice=product.unitPrice,
            quantity=quantity,
        )

        new_items = order.items + [new_item]
        updated = order.model_copy(
            update={
                "items": new_items,
                "totalAmount": self._calculate_total(new_items),
            }
        )
        return self.repo.update_order(order_id, updated)

    def update_item_quantity(
        self, order_id: int, item_id: int, quantity: int
    ) -> Optional[Order]:
        order = self.repo.find_order_by_id(order_id)
        if not order:
            return None

        item = next((i for i in order.items if i.id == item_id), None)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with ID {item_id} not found in order {order_id}",
            )

        new_items = [
            i.model_copy(update={"quantity": quantity}) if i.id == item_id else i
            for i in order.items
        ]
        updated = order.model_copy(
            update={
                "items": new_items,
                "totalAmount": self._calculate_total(new_items),
            }
        )
        return self.repo.update_order(order_id, updated)

    def remove_item_from_order(
        self, order_id: int, item_id: int
    ) -> Optional[Order]:
        order = self.repo.find_order_by_id(order_id)
        if not order:
            return None

        new_items = [i for i in order.items if i.id != item_id]
        updated = order.model_copy(
            update={
                "items": new_items,
                "totalAmount": self._calculate_total(new_items),
            }
        )
        return self.repo.update_order(order_id, updated)

    # ─── Products ─────────────────────────────────────────────────

    def get_all_products(self) -> list[Product]:
        return self.repo.find_all_products()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.repo.find_product_by_id(product_id)
