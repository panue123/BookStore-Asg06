from dataclasses import dataclass, field


@dataclass
class CreateVariantCommand:
    product_id: int
    name: str
    sku: str
    price: float
    stock: int = 0
    attributes: dict = field(default_factory=dict)
