from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Brand:
    id: Optional[int]
    name: str       # "NXB Kim Đồng", "NXB Trẻ", ...
    slug: str
    logo_url: str = ""
