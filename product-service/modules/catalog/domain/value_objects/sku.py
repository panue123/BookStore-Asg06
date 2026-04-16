from __future__ import annotations
import re


class SKU:
    """Value object: Stock Keeping Unit."""
    def __init__(self, value: str):
        value = value.strip().upper()
        if not re.match(r'^[A-Z0-9\-]{3,32}$', value):
            raise ValueError(f"Invalid SKU: {value}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        return isinstance(other, SKU) and self._value == other._value
