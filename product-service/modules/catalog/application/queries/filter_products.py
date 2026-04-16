from dataclasses import dataclass
from typing import Optional


@dataclass
class FilterProductsQuery:
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    limit: int = 20
    offset: int = 0
