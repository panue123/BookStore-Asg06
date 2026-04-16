"""JSON attributes value object — linh hoạt cho mọi loại sản phẩm."""
from __future__ import annotations
from typing import Any


class Attributes:
    """
    Wrapper cho JSONB attributes.
    Ví dụ sách: {"author": "...", "pages": 300, "publisher": "NXB Trẻ"}
    """
    def __init__(self, data: dict | None = None):
        self._data: dict = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> "Attributes":
        return Attributes({**self._data, key: value})

    def to_dict(self) -> dict:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Attributes({self._data})"
