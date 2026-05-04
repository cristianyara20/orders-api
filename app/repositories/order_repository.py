"""
Repositorio de datos – Carga el archivo Orders.json y gestiona
la persistencia en memoria (equivalente al OrderRepository de TS).
"""

import json
from pathlib import Path
from typing import Optional

from app.models.schemas import Order, Customer, Product, Supplier, OrderItem


class OrderRepository:
    """Acceso a datos en memoria, usando Orders.json como semilla."""

    def __init__(self) -> None:
        self.orders: list[Order] = []
        self.customers: list[Customer] = []
        self.products: list[Product] = []
        self.suppliers: list[Supplier] = []
        self._load_data()

    # ─── Carga inicial ────────────────────────────────────────────

    def _load_data(self) -> None:
        json_path = Path(__file__).resolve().parent.parent.parent / "Orders.json"
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            self.orders = [Order(**o) for o in raw_data]
            self._normalize_data()
            print("[OK] Data loaded successfully from Orders.json")
        except Exception as e:
            print(f"[ERROR] Error loading Orders.json: {e}")
            self.orders = []

    def _normalize_data(self) -> None:
        """Extrae listas únicas de clientes, productos y proveedores."""
        customer_map: dict[int, Customer] = {}
        product_map: dict[int, Product] = {}
        supplier_map: dict[int, Supplier] = {}

        for order in self.orders:
            if order.customer:
                customer_map[order.customer.id] = order.customer

            for item in order.items:
                if item.product:
                    product_map[item.product.id] = item.product
                    if item.product.supplier:
                        supplier_map[item.product.supplier.id] = item.product.supplier

        self.customers = list(customer_map.values())
        self.products = list(product_map.values())
        self.suppliers = list(supplier_map.values())

    # ─── Orders ───────────────────────────────────────────────────

    def find_all_orders(self) -> list[Order]:
        return self.orders

    def find_order_by_id(self, order_id: int) -> Optional[Order]:
        return next((o for o in self.orders if o.id == order_id), None)

    def save_order(self, order: Order) -> Order:
        self.orders.append(order)
        return order

    def update_order(self, order_id: int, order_data: Order) -> Optional[Order]:
        for i, o in enumerate(self.orders):
            if o.id == order_id:
                self.orders[i] = order_data
                return self.orders[i]
        return None

    def delete_order(self, order_id: int) -> bool:
        for i, o in enumerate(self.orders):
            if o.id == order_id:
                self.orders.pop(i)
                return True
        return False

    # ─── Customers ────────────────────────────────────────────────

    def find_all_customers(self) -> list[Customer]:
        return self.customers

    # ─── Products ─────────────────────────────────────────────────

    def find_all_products(self) -> list[Product]:
        return self.products

    def find_product_by_id(self, product_id: int) -> Optional[Product]:
        return next((p for p in self.products if p.id == product_id), None)
