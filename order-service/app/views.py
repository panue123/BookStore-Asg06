import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem, OrderStatus
from .serializers import OrderSerializer, OrderItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Create a new order from cart and process payment"""
        customer_id = request.data.get('customer_id')
        shipping_address = request.data.get('shipping_address', '')
        cart_id = request.data.get('cart_id')
        payment_method = request.data.get('payment_method', 'credit_card')

        if not customer_id or not cart_id:
            return Response({'error': 'customer_id and cart_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Get Cart Details
            cart_resp = requests.get(f'http://cart-service:8000/api/carts/{cart_id}/')
            if cart_resp.status_code != 200:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

            cart_data = cart_resp.json()
            items = cart_data.get('items', [])
            
            if not items:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Calculate Total & Create Order
            total_amount = sum(float(item['price_at_add']) * item['quantity'] for item in items if item['price_at_add'])
            
            order = Order.objects.create(
                customer_id=customer_id,
                total_amount=total_amount,
                shipping_address=shipping_address,
                status=OrderStatus.PENDING
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    book_id=item['book_id'],
                    quantity=item['quantity'],
                    price=item['price_at_add']
                )

            # 3. Trigger Payment Service
            try:
                pay_resp = requests.post('http://pay-service:8000/api/payments/process/', data={
                    'order_id': order.id,
                    'amount': total_amount,
                    'payment_method': payment_method
                })
                
                if pay_resp.status_code == 200:
                    payment_data = pay_resp.json()
                    if payment_data.get('status') == 'success':
                        order.status = OrderStatus.PAID
                        order.save()
                        
                        # 4. Trigger Shipping Service if paid
                        try:
                            requests.post('http://ship-service:8000/api/shipments/create_shipment/', data={
                                'order_id': order.id,
                                'address': shipping_address,
                                'customer_id': customer_id
                            })
                        except:
                            pass

                        # 5. Clear Cart items
                        for item in items:
                            try:
                                requests.post(f'http://cart-service:8000/api/carts/{cart_id}/update_item_quantity/', data={
                                    'book_id': item['book_id'],
                                    'quantity': 0
                                })
                            except:
                                pass
            except:
                pass

            return Response({
                'message': 'Order created successfully',
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """Get all orders for a customer"""
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response({'error': 'customer_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response({
            'customer_id': customer_id,
            'count': len(orders),
            'orders': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def order_details(self, request, pk=None):
        """Get detailed information about an order"""
        order = self.get_object()
        serializer = self.get_serializer(order)
        items = OrderItem.objects.filter(order=order)
        items_serializer = OrderItemSerializer(items, many=True)
        
        return Response({
            'order': serializer.data,
            'items': items_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify_purchase(self, request):
        """Verify if a customer has purchased a specific book"""
        customer_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        
        if not customer_id or not book_id:
            return Response({'error': 'customer_id and book_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if customer has a paid order containing this book
        order_items = OrderItem.objects.filter(
            order__customer_id=customer_id,
            order__status=OrderStatus.PAID,
            book_id=book_id
        )
        
        if order_items.exists():
            return Response({
                'customer_id': customer_id,
                'book_id': book_id,
                'purchased': True,
                'purchase_count': order_items.count(),
                'total_quantity': sum(item.quantity for item in order_items)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'customer_id': customer_id,
                'book_id': book_id,
                'purchased': False
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel an order if it hasn't been shipped"""
        order = self.get_object()
        
        if order.status == OrderStatus.SHIPPED:
            return Response({'error': 'Cannot cancel shipped orders'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = OrderStatus.CANCELED
        order.save()
        
        return Response({
            'message': 'Order canceled successfully',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
