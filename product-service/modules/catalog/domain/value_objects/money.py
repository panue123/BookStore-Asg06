from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "VND"

    def __add__(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount:,.0f} {self.currency}"
