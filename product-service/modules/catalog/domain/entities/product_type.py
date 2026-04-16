from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductType:
    """Định nghĩa schema attributes cho từng loại sản phẩm."""
    id: Optional[int]
    name: str                               # "Sách", "Ebook", "Audiobook"
    attribute_schema: dict = field(default_factory=dict)  # {"author": "str", "pages": "int"}
