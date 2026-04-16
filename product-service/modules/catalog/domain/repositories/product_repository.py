"""Abstract repository interface — domain không phụ thuộc ORM."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]: ...

    @abstractmethod
    def list_all(self, limit: int = 20, offset: int = 0) -> list[Product]: ...

    @abstractmethod
    def filter(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]: ...

    @abstractmethod
    def save(self, product: Product) -> Product: ...

    @abstractmethod
    def delete(self, product_id: int) -> None: ...

    @abstractmethod
    def count(self, category_id: int | None = None) -> int: ...
