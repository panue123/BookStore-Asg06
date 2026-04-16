from dataclasses import dataclass, field


@dataclass
class CreateProductCommand:
    name: str
    category_id: int
    price: float
    attributes: dict = field(default_factory=dict)
    stock: int = 0
    description: str = ""
    cover_image: str = ""
