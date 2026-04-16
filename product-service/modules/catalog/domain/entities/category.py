"""Category tree entity — category là dữ liệu, không phải enum."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    name: str                       # "lập trình", "khoa học", ...
    slug: str                       # "lap-trinh", "khoa-hoc", ...
    parent_id: Optional[int] = None
    description: str = ""
    icon: str = ""

    def is_root(self) -> bool:
        return self.parent_id is None
