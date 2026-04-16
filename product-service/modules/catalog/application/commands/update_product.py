from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UpdateProductCommand:
    product_id: int
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    attributes: Optional[dict] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
