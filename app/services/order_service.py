"""
Capa de lógica de negocio – Equivalente al OrderService de TypeScript.
Contiene las validaciones y el cálculo automático de totalAmount.
"""

import random
import time
from typing import Optional

from fastapi import HTTPException, status

from app.models.schemas import Order, OrderItem, Product, Customer, Supplier
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

    def get_orders_paginated(
        self, page: int, limit: int, customer_id: Optional[int], date_from: Optional[str], date_to: Optional[str], sort: Optional[str]
    ) -> dict:
        items, total = self.repo.find_orders_paginated(page, limit, customer_id, date_from, date_to, sort)
        return {"total": total, "page": page, "limit": limit, "items": items}

    def get_all_orders(self) -> list[Order]:
        return self.repo.find_all_orders()

    def get_orders_by_customer(self, customer_id: int) -> list[Order]:
        """Return orders filtered by customer ID."""
        return [o for o in self.repo.find_all_orders() if o.customer and o.customer.id == customer_id]

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

    def get_products_paginated(
        self, page: int, limit: int, supplier_id: Optional[int], search: Optional[str], discontinued: Optional[bool], sort: Optional[str]
    ) -> dict:
        items, total = self.repo.find_products_paginated(page, limit, supplier_id, search, discontinued, sort)
        return {"total": total, "page": page, "limit": limit, "items": items}

    def get_all_products(self) -> list[Product]:
        return self.repo.find_all_products()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.repo.find_product_by_id(product_id)

    def create_product(self, data: dict) -> Product:
        supplier = None
        if data.get("supplierId"):
            supplier = self.repo.find_supplier_by_id(data["supplierId"])
            if not supplier:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier not found")
        
        new_product = Product(
            id=self._generate_id(),
            productName=data["productName"],
            unitPrice=data["unitPrice"],
            package=data["package"],
            isDiscontinued=data.get("isDiscontinued", False),
            supplier=supplier
        )
        return self.repo.create_product(new_product)

    def replace_product(self, product_id: int, data: dict) -> Optional[Product]:
        existing = self.repo.find_product_by_id(product_id)
        if not existing:
            return None
        
        supplier = None
        if data.get("supplierId"):
            supplier = self.repo.find_supplier_by_id(data["supplierId"])
            if not supplier:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier not found")

        updated_data = data.copy()
        if "supplierId" in updated_data:
            del updated_data["supplierId"]
        updated_data["supplier"] = supplier

        return self.repo.update_product(product_id, updated_data)

    def update_product(self, product_id: int, data: dict) -> Optional[Product]:
        existing = self.repo.find_product_by_id(product_id)
        if not existing:
            return None
            
        updates = data.copy()
        if "supplierId" in updates:
            supplier = self.repo.find_supplier_by_id(updates["supplierId"])
            if not supplier and updates["supplierId"] is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier not found")
            updates["supplier"] = supplier
            del updates["supplierId"]

        return self.repo.update_product(product_id, updates)

    def delete_product(self, product_id: int) -> bool:
        return self.repo.delete_product(product_id)

    # ─── Customers ────────────────────────────────────────────────

    def get_customers_paginated(
        self, page: int, limit: int, country: Optional[str], city: Optional[str], search: Optional[str], sort: Optional[str]
    ) -> dict:
        items, total = self.repo.find_customers_paginated(page, limit, country, city, search, sort)
        return {"total": total, "page": page, "limit": limit, "items": items}

    def get_all_customers(self) -> list[Customer]:
        return self.repo.find_all_customers()

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.repo.find_customer_by_id(customer_id)

    def create_customer(self, data: dict) -> Customer:
        new_customer = Customer(
            id=self._generate_id(),
            firstName=data["firstName"],
            lastName=data["lastName"],
            city=data["city"],
            country=data["country"],
            phone=data["phone"]
        )
        return self.repo.create_customer(new_customer)

    def update_customer(self, customer_id: int, data: dict) -> Optional[Customer]:
        return self.repo.update_customer(customer_id, data)

    # ─── Suppliers ────────────────────────────────────────────────

    def get_suppliers_paginated(
        self, page: int, limit: int, country: Optional[str], city: Optional[str], search: Optional[str], sort: Optional[str]
    ) -> dict:
        items, total = self.repo.find_suppliers_paginated(page, limit, country, city, search, sort)
        return {"total": total, "page": page, "limit": limit, "items": items}

    def get_all_suppliers(self) -> list[Supplier]:
        return self.repo.find_all_suppliers()

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        return self.repo.find_supplier_by_id(supplier_id)

    def get_products_by_supplier(self, supplier_id: int) -> list[Product]:
        return self.repo.find_products_by_supplier(supplier_id)

    def create_supplier(self, data: dict) -> Supplier:
        new_supplier = Supplier(
            id=self._generate_id(),
            companyName=data["companyName"],
            contactName=data["contactName"],
            contactTitle=data["contactTitle"],
            city=data["city"],
            country=data["country"],
            phone=data["phone"],
            fax=data.get("fax")
        )
        return self.repo.create_supplier(new_supplier)

    def update_supplier(self, supplier_id: int, data: dict) -> Optional[Supplier]:
        return self.repo.update_supplier(supplier_id, data)
