from django.db import models


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def by_category(self, category_id: int):
        return self.filter(category_id=category_id)

    def in_stock(self):
        return self.filter(stock__gt=0)

    def price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs

    def search(self, query: str):
        return self.filter(name__icontains=query)
