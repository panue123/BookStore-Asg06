import os
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        # Support both product_id (new) and book_id (legacy)
        product_id = request.data.get('product_id') or request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Call product-service to get product details
        try:
            resp = requests.get(
                f'{PRODUCT_SERVICE_URL}/api/products/{product_id}/',
                timeout=8,
            )
            if resp.status_code != 200:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            product_data = resp.json()
            price = product_data.get('price')

            if product_data.get('stock', 0) < quantity:
                return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Failed to communicate with Product Service: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=product_id,   # keep field name for DB compat
            defaults={'price_at_add': price, 'quantity': quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price_at_add = price
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def update_item_quantity(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id') or request.data.get('book_id')
        quantity = int(request.data.get('quantity', 0))

        try:
            item = CartItem.objects.get(cart=cart, book_id=product_id)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)