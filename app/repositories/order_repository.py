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

    def find_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        return next((c for c in self.customers if c.id == customer_id), None)

    def find_all_suppliers(self) -> list[Supplier]:
        return self.suppliers

    # ─── Products ─────────────────────────────────────────────────

    def find_all_products(self) -> list[Product]:
        return self.products

    def find_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        return next((s for s in self.suppliers if s.id == supplier_id), None)


    # ─── Helper de paginación genérica ────────────────────────────────────────
    @staticmethod
    def _paginate(data: list, page: int, limit: int) -> tuple[list, int]:
        """Devuelve sub‑lista y total según page/limit.
        page >= 1, limit >= 1.
        """
        total = len(data)
        start = (page - 1) * limit
        end = start + limit
        return data[start:end], total

    # ─── Listados paginados ───────────────────────────────────────────────────
    def find_orders_paginated(self, page: int = 1, limit: int = 20,
                               customer_id: int | None = None,
                               date_from: str | None = None,
                               date_to: str | None = None,
                               sort: str | None = None) -> tuple[list[Order], int]:
        """Aplica filtros, ordenamiento y paginación a la lista de órdenes.
        `sort` puede ser "field" o "-field" (desc)."""
        data = self.orders
        if customer_id is not None:
            data = [o for o in data if o.customer and o.customer.id == customer_id]
        if date_from is not None:
            data = [o for o in data if o.orderDate >= date_from]
        if date_to is not None:
            data = [o for o in data if o.orderDate <= date_to]
        if sort:
            reverse = sort.startswith('-')
            key = sort.lstrip('-')
            data = sorted(data, key=lambda o: getattr(o, key, None), reverse=reverse)
        return self._paginate(data, page, limit)

    def find_products_paginated(self, page: int = 1, limit: int = 20,
                                 supplier_id: int | None = None,
                                 search: str | None = None,
                                 discontinued: bool | None = None,
                                 sort: str | None = None) -> tuple[list[Product], int]:
        data = self.products
        if supplier_id is not None:
            data = [p for p in data if p.supplier and p.supplier.id == supplier_id]
        if search:
            lc = search.lower()
            data = [p for p in data if lc in p.productName.lower()]
        if discontinued is not None:
            data = [p for p in data if p.isDiscontinued == discontinued]
        if sort:
            reverse = sort.startswith('-')
            key = sort.lstrip('-')
            data = sorted(data, key=lambda p: getattr(p, key, None), reverse=reverse)
        return self._paginate(data, page, limit)

    def find_customers_paginated(self, page: int = 1, limit: int = 20,
                                 country: str | None = None,
                                 city: str | None = None,
                                 search: str | None = None,
                                 sort: str | None = None) -> tuple[list[Customer], int]:
        data = self.customers
        if country:
            data = [c for c in data if c.country.lower() == country.lower()]
        if city:
            data = [c for c in data if c.city.lower() == city.lower()]
        if search:
            lc = search.lower()
            data = [c for c in data if lc in c.firstName.lower() or lc in c.lastName.lower()]
        if sort:
            reverse = sort.startswith('-')
            key = sort.lstrip('-')
            data = sorted(data, key=lambda c: getattr(c, key, None), reverse=reverse)
        return self._paginate(data, page, limit)

    def find_suppliers_paginated(self, page: int = 1, limit: int = 20,
                                 country: str | None = None,
                                 city: str | None = None,
                                 search: str | None = None,
                                 sort: str | None = None) -> tuple[list[Supplier], int]:
        data = self.suppliers
        if country:
            data = [s for s in data if s.country.lower() == country.lower()]
        if city:
            data = [s for s in data if s.city.lower() == city.lower()]
        if search:
            lc = search.lower()
            data = [s for s in data if lc in s.companyName.lower()]
        if sort:
            reverse = sort.startswith('-')
            key = sort.lstrip('-')
            data = sorted(data, key=lambda s: getattr(s, key, None), reverse=reverse)
        return self._paginate(data, page, limit)



    # ─── CRUD para Customers ────────────────────────────────────────────────
    def create_customer(self, customer: Customer) -> Customer:
        """Add a new customer and return it."""
        self.customers.append(customer)
        return customer

    def update_customer(self, customer_id: int, data: dict) -> Optional[Customer]:
        """Update an existing customer with partial data and return it."""
        for i, c in enumerate(self.customers):
            if c.id == customer_id:
                updated = c.model_copy(update=data)
                self.customers[i] = updated
                return updated
        return None

    def delete_customer(self, customer_id: int) -> bool:
        """Remove a customer by id. Returns True if deleted."""
        for i, c in enumerate(self.customers):
            if c.id == customer_id:
                self.customers.pop(i)
                return True
        return False

    # ─── CRUD para Products ────────────────────────────────────────────────────
    def create_product(self, product: Product) -> Product:
        """Add a new product and return it."""
        self.products.append(product)
        return product

    def update_product(self, product_id: int, data: dict) -> Optional[Product]:
        """Update a product partially and return it."""
        for i, p in enumerate(self.products):
            if p.id == product_id:
                updated = p.model_copy(update=data)
                self.products[i] = updated
                return updated
        return None

    def delete_product(self, product_id: int) -> bool:
        """Delete a product. Returns True if removed."""
        for i, p in enumerate(self.products):
            if p.id == product_id:
                self.products.pop(i)
                return True
        return False

    # ─── CRUD para Suppliers ────────────────────────────────────────────────────
    def create_supplier(self, supplier: Supplier) -> Supplier:
        """Add a new supplier and return it."""
        self.suppliers.append(supplier)
        return supplier

    def update_supplier(self, supplier_id: int, data: dict) -> Optional[Supplier]:
        """Update a supplier partially and return it."""
        for i, s in enumerate(self.suppliers):
            if s.id == supplier_id:
                updated = s.model_copy(update=data)
                self.suppliers[i] = updated
                return updated
        return None

    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete a supplier. Returns True if removed."""
        for i, s in enumerate(self.suppliers):
            if s.id == supplier_id:
                self.suppliers.pop(i)
                return True
        return False
