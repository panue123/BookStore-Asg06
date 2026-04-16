"""Concrete repository — Django ORM implementation."""
from __future__ import annotations
from typing import Optional
from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ..models.product_model import ProductModel


def _to_entity(m: ProductModel) -> Product:
    return Product(
        id=m.id,
        name=m.name,
        category_id=m.category_id,
        price=float(m.price),
        attributes=m.attributes or {},
        stock=m.stock,
        description=m.description,
        cover_image=m.cover_image,
        is_active=m.is_active,
    )


def _to_model_data(p: Product) -> dict:
    return {
        'name':        p.name,
        'category_id': p.category_id,
        'price':       p.price,
        'attributes':  p.attributes,
        'stock':       p.stock,
        'description': p.description,
        'cover_image': p.cover_image,
        'is_active':   p.is_active,
    }


class DjangoProductRepository(ProductRepository):
    def get_by_id(self, product_id: int) -> Optional[Product]:
        try:
            return _to_entity(ProductModel.objects.get(pk=product_id, is_active=True))
        except ProductModel.DoesNotExist:
            return None

    def list_all(self, limit: int = 20, offset: int = 0) -> list[Product]:
        qs = ProductModel.objects.filter(is_active=True)[offset:offset + limit]
        return [_to_entity(m) for m in qs]

    def filter(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        qs = ProductModel.objects.filter(is_active=True)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        if search:
            qs = qs.filter(name__icontains=search)
        return [_to_entity(m) for m in qs[offset:offset + limit]]

    def save(self, product: Product) -> Product:
        data = _to_model_data(product)
        if product.id:
            ProductModel.objects.filter(pk=product.id).update(**data)
            return _to_entity(ProductModel.objects.get(pk=product.id))
        m = ProductModel.objects.create(**data)
        return _to_entity(m)

    def delete(self, product_id: int) -> None:
        ProductModel.objects.filter(pk=product_id).update(is_active=False)

    def count(self, category_id: int | None = None) -> int:
        qs = ProductModel.objects.filter(is_active=True)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs.count()
