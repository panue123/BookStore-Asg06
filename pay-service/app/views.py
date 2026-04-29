import os
import uuid
import logging
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment, PaymentStatus
from .serializers import PaymentSerializer, PaymentProcessSerializer, PaymentRefundSerializer


logger = logging.getLogger(__name__)
ORDER_SVC = os.getenv('ORDER_SERVICE_URL', 'http://order-service:8000')
USER_SVC = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')
NOTIFICATION_SVC = os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:8000')


def _notify_customer(order_id, subject, message, metadata=None):
    customer_id = None
    recipient = f'order-{order_id}'
    try:
        order_resp = requests.get(f'{ORDER_SVC}/api/orders/{order_id}/', timeout=5)
        if order_resp.status_code == 200:
            order_data = order_resp.json().get('order') or order_resp.json()
            customer_id = order_data.get('customer_id')
            if customer_id:
                try:
                    user_resp = requests.get(f'{USER_SVC}/api/users/{customer_id}/', timeout=5)
                    if user_resp.status_code == 200:
                        user_data = user_resp.json()
                        recipient = user_data.get('email') or user_data.get('username') or recipient
                except requests.RequestException:
                    recipient = f'user-{customer_id}'
    except requests.RequestException:
        pass

    payload = {
        'user_id': customer_id,
        'channel': 'email',
        'recipient': recipient,
        'subject': subject,
        'message': message,
        'metadata': metadata or {},
    }
    try:
        requests.post(f'{NOTIFICATION_SVC}/api/notifications/', json=payload, timeout=5)
    except requests.RequestException:
        logger.warning('Notification service unavailable for order %s', order_id)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process a payment for an order"""
        serializer = PaymentProcessSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['amount']
            payment_method = serializer.validated_data.get('payment_method', 'credit_card')
            
            # Create payment record
            payment = Payment.objects.create(
                order_id=order_id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=str(uuid.uuid4()),  # Simulate transaction ID
                status=PaymentStatus.PENDING
            )
            
            # Simulate payment processing
            try:
                if amount > 0:
                    payment.status = PaymentStatus.SUCCESS
                    payment.save()
                    _notify_customer(
                        order_id,
                        f'Thanh toán đơn hàng #{order_id} thành công',
                        f'Đơn thanh toán cho đơn hàng #{order_id} đã được xử lý thành công với số tiền {amount}.',
                        {
                            'event': 'payment.success',
                            'order_id': order_id,
                            'payment_id': payment.id,
                            'transaction_id': payment.transaction_id,
                        },
                    )
                    return Response({
                        'status': 'success',
                        'message': 'Payment processed successfully',
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_200_OK)
                else:
                    payment.status = PaymentStatus.FAILED
                    payment.save()
                    _notify_customer(
                        order_id,
                        f'Thanh toán đơn hàng #{order_id} thất bại',
                        f'Đơn thanh toán cho đơn hàng #{order_id} không hợp lệ vì số tiền không hợp lệ.',
                        {
                            'event': 'payment.failed',
                            'order_id': order_id,
                            'payment_id': payment.id,
                            'transaction_id': payment.transaction_id,
                        },
                    )
                    return Response({'error': 'Invalid amount', 'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                payment.status = PaymentStatus.FAILED
                payment.save()
                _notify_customer(
                    order_id,
                    f'Thanh toán đơn hàng #{order_id} thất bại',
                    f'Đã xảy ra lỗi khi xử lý thanh toán cho đơn hàng #{order_id}: {e}.',
                    {
                        'event': 'payment.failed',
                        'order_id': order_id,
                        'payment_id': payment.id,
                        'transaction_id': payment.transaction_id,
                    },
                )
                return Response({'error': str(e), 'status': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """Get payment details for a specific order"""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'error': 'order_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(order_id=order_id)
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment"""
        payment = self.get_object()
        
        if payment.status != PaymentStatus.SUCCESS:
            return Response({'error': 'Only successful payments can be refunded'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment.status = PaymentStatus.REFUNDED
            payment.save()
            _notify_customer(
                payment.order_id,
                f'Hoàn tiền đơn hàng #{payment.order_id} thành công',
                f'Khoản thanh toán cho đơn hàng #{payment.order_id} đã được hoàn tiền thành công.',
                {
                    'event': 'payment.refunded',
                    'order_id': payment.order_id,
                    'payment_id': payment.id,
                },
            )
            return Response({
                'message': 'Payment refunded successfully',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get payment status"""
        transaction_id = request.query_params.get('transaction_id')
        if not transaction_id:
            return Response({'error': 'transaction_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            return Response({
                'transaction_id': payment.transaction_id,
                'order_id': payment.order_id,
                'amount': payment.amount,
                'status': payment.status,
                'payment_method': payment.payment_method,
                'created_at': payment.created_at,
                'updated_at': payment.updated_at
            }, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        payment = self.get_object()
        
        if payment.status != PaymentStatus.SUCCESS:
            return Response({'error': 'Only paid payments can be refunded'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PaymentRefundSerializer(data=request.data)
        if serializer.is_valid():
            # Simulate refund processing
            payment.status = PaymentStatus.REFUNDED
            payment.save()
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def check_status(self, request):
        """Check payment status by order_id"""
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(order_id=order_id)
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
