"""Application service — orchestrates use cases."""
from __future__ import annotations
from typing import Optional
from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository):
        self._repo = repo

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_product(self, product_id: int) -> Optional[Product]:
        return self._repo.get_by_id(product_id)

    def list_products(self, limit: int = 20, offset: int = 0) -> list[Product]:
        return self._repo.list_all(limit=limit, offset=offset)

    def filter_products(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        return self._repo.filter(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            search=search,
            limit=limit,
            offset=offset,
        )

    def count_products(self, category_id: int | None = None) -> int:
        return self._repo.count(category_id=category_id)

    # ── Commands ──────────────────────────────────────────────────────────────

    def create_product(
        self,
        name: str,
        category_id: int,
        price: float,
        attributes: dict | None = None,
        stock: int = 0,
        description: str = "",
        cover_image: str = "",
    ) -> Product:
        product = Product(
            id=None,
            name=name,
            category_id=category_id,
            price=price,
            attributes=attributes or {},
            stock=stock,
            description=description,
            cover_image=cover_image,
        )
        return self._repo.save(product)

    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        product = self._repo.get_by_id(product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        return self._repo.save(product)

    def delete_product(self, product_id: int) -> None:
        self._repo.delete(product_id)
