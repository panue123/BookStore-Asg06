from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ....infrastructure.models.product_model import ProductModel
from ....infrastructure.repositories.product_repository_impl import DjangoProductRepository
from ....application.services.product_service import ProductService
from ..serializers.product_serializer import ProductSerializer

_repo    = DjangoProductRepository()
_service = ProductService(_repo)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.filter(is_active=True).select_related(
        'category', 'brand', 'product_type'
    ).prefetch_related('variants')
    serializer_class = ProductSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'product_type', 'is_active']
    search_fields    = ['name', 'description', 'sku', 'attributes__author',
                        'attributes__brand', 'category__name']
    ordering_fields  = ['price', 'created_at', 'name', 'stock']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        category_slug = params.get('category_slug')
        product_type  = params.get('product_type_name')
        in_stock      = params.get('in_stock')

        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if product_type:
            qs = qs.filter(product_type__name=product_type)
        if in_stock and in_stock.lower() in ('true', '1'):
            qs = qs.filter(stock__gt=0)
        return qs

    @action(detail=False, methods=['get'], url_path='filter')
    def filter_products(self, request):
        """GET /api/products/filter?category_slug=books-programming&min_price=100000"""
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ProductSerializer(page, many=True).data)
        return Response(ProductSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[0-9]+)')
    def by_category(self, request, category_id=None):
        products = _service.filter_products(category_id=int(category_id))
        data = [
            {'id': p.id, 'name': p.name, 'sku': p.sku, 'price': p.price,
             'stock': p.stock, 'attributes': p.attributes}
            for p in products
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """GET /api/products/search?q=laptop&category_slug=electronics"""
        q = request.query_params.get('q', '')
        qs = self.get_queryset()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ProductSerializer(page, many=True).data)
        return Response(ProductSerializer(qs, many=True).data)
