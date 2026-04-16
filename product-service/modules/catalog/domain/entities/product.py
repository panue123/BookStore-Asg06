"""Product core entity — pure domain logic, no framework dependency."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """
    Core product entity — tổng quát cho mọi domain sản phẩm.
    Category là dữ liệu (category_id), không phải enum cứng.
    attributes là JSONB — linh hoạt cho mọi loại sản phẩm:
      - Sách: {"author": "...", "pages": 300, "isbn": "..."}
      - Điện tử: {"brand": "Samsung", "ram": "8GB", "storage": "256GB"}
      - Thời trang: {"material": "Cotton", "gender": "Unisex"}
    """
    id: Optional[int]
    name: str
    category_id: int
    price: float                        # VNĐ
    sku: str = ""                       # Stock Keeping Unit
    attributes: dict = field(default_factory=dict)
    stock: int = 0
    description: str = ""
    cover_image: str = ""
    is_active: bool = True
    brand_id: Optional[int] = None
    product_type_id: Optional[int] = None

    def is_in_stock(self) -> bool:
        return self.stock > 0

    def apply_discount(self, percent: float) -> float:
        """Trả về giá sau giảm, không mutate entity."""
        return round(self.price * (1 - percent / 100), 0)

    def get_attribute(self, key: str, default=None):
        return self.attributes.get(key, default)
