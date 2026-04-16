"""Variant entity — biến thể sản phẩm (bìa cứng/mềm, phiên bản, ...)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Variant:
    id: Optional[int]
    product_id: int
    name: str                           # "Bìa cứng", "Bìa mềm", "Tái bản lần 3"
    sku: str
    price: float
    stock: int = 0
    attributes: dict = field(default_factory=dict)  # {"binding": "hardcover"}
