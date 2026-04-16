from dataclasses import dataclass


@dataclass
class ListProductsQuery:
    limit: int = 20
    offset: int = 0
