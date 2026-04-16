from dataclasses import dataclass


@dataclass
class GetProductQuery:
    product_id: int
