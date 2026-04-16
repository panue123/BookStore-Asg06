import os
import requests
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Manager, InventoryLog, SalesReport
from .serializers import ManagerSerializer, InventoryLogSerializer, SalesReportSerializer

PRODUCT_SVC = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")


def _extract(data):
    if isinstance(data, list): return data
    if isinstance(data, dict): return data.get('results', data.get('orders', data.get('products', data.get('shipments', []))))
    return []


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    @action(detail=False, methods=['post'])
    def dashboard(self, request):
        try:
            orders_resp = requests.get('http://order-service:8000/api/orders/', timeout=8)
            total_orders, total_revenue = 0, 0
            if orders_resp.status_code == 200:
                orders = _extract(orders_resp.json())
                total_orders = len(orders)
                total_revenue = sum(float(o.get('total_amount', 0)) for o in orders if o)

            products_resp = requests.get(f'{PRODUCT_SVC}/api/products/?page_size=1000', timeout=8)
            total_products, low_stock_items = 0, []
            if products_resp.status_code == 200:
                products = _extract(products_resp.json())
                total_products = len(products)
                for p in products:
                    if isinstance(p, dict) and p.get('stock', 0) < 10:
                        low_stock_items.append({'id': p.get('id'), 'title': p.get('name') or p.get('title'), 'stock': p.get('stock')})

            customers_resp = requests.get('http://customer-service:8000/api/customers/', timeout=8)
            total_customers = 0
            if customers_resp.status_code == 200:
                cdata = customers_resp.json()
                total_customers = cdata.get('count', len(_extract(cdata))) if isinstance(cdata, dict) else len(_extract(cdata))

            return Response({'dashboard': {
                'total_orders': total_orders, 'total_revenue': float(total_revenue),
                'total_products': total_products, 'total_customers': total_customers,
                'low_stock_items': low_stock_items, 'timestamp': datetime.now().isoformat(),
            }})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_inventory(self, request):
        product_id = request.data.get('product_id') or request.data.get('book_id')
        new_stock  = request.data.get('new_stock')
        reason     = request.data.get('reason', 'Manual adjustment')
        manager_id = request.data.get('manager_id')
        if not product_id or new_stock is None:
            return Response({'error': 'product_id and new_stock are required'}, status=400)
        try:
            prod_resp = requests.get(f'{PRODUCT_SVC}/api/products/{product_id}/', timeout=8)
            if prod_resp.status_code != 200:
                return Response({'error': 'Product not found'}, status=404)
            prod_data = prod_resp.json()
            previous_stock = prod_data.get('stock', 0)
            update_resp = requests.patch(f'{PRODUCT_SVC}/api/products/{product_id}/', json={'stock': new_stock}, timeout=8)
            if update_resp.status_code in (200, 201):
                manager = None
                if manager_id:
                    try: manager = Manager.objects.get(id=manager_id)
                    except Manager.DoesNotExist: pass
                log = InventoryLog.objects.create(
                    book_id=product_id,
                    book_title=prod_data.get('name') or prod_data.get('title', ''),
                    previous_stock=previous_stock, new_stock=new_stock,
                    change_amount=new_stock - previous_stock, reason=reason, created_by=manager,
                )
                return Response({'message': 'Inventory updated', 'log': InventoryLogSerializer(log).data})
            return Response({'error': 'Failed to update stock'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def inventory_logs(self, request):
        limit = int(request.query_params.get('limit', 20))
        logs = InventoryLog.objects.all().order_by('-created_at')[:limit]
        return Response({'count': len(logs), 'logs': InventoryLogSerializer(logs, many=True).data})

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        try:
            resp = requests.get('http://order-service:8000/api/orders/', timeout=8)
            if resp.status_code != 200:
                return Response({'error': 'Failed to fetch orders'}, status=503)
            orders = _extract(resp.json())
            paid = [o for o in orders if o.get('status') == 'paid']
            total = sum(float(o.get('total_amount', 0)) for o in paid)
            return Response({'total_orders': len(orders), 'paid_orders': len(paid),
                             'total_sales': total, 'average_order_value': total / len(paid) if paid else 0})
        except Exception as e:
            return Response({'error': str(e)}, status=503)

    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        try:
            resp = requests.get(f'{PRODUCT_SVC}/api/products/?page_size=1000', timeout=8)
            if resp.status_code != 200:
                return Response({'error': 'Failed to fetch products'}, status=503)
            products = _extract(resp.json())
            return Response({
                'total_products': len(products),
                'in_stock': len([p for p in products if p.get('stock', 0) > 0]),
                'out_of_stock': len([p for p in products if p.get('stock', 0) == 0]),
                'total_inventory_value': sum(float(p.get('price', 0)) * p.get('stock', 0) for p in products),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=503)

    @action(detail=False, methods=['get'])
    def shipping_report(self, request):
        try:
            resp = requests.get('http://ship-service:8000/api/shipments/', timeout=8)
            if resp.status_code != 200:
                return Response({'error': 'Failed to fetch shipments'}, status=503)
            shipments = _extract(resp.json())
            return Response({
                'total_shipments': len(shipments),
                'shipped':   len([s for s in shipments if s.get('status') == 'shipped']),
                'delivered': len([s for s in shipments if s.get('status') == 'delivered']),
                'pending':   len([s for s in shipments if s.get('status') in ['pending', 'processing']]),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=503)

    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        threshold = int(request.query_params.get('threshold', 10))
        try:
            resp = requests.get(f'{PRODUCT_SVC}/api/products/?page_size=1000', timeout=8)
            if resp.status_code != 200:
                return Response({'error': 'Failed to fetch products'}, status=503)
            data = resp.json()
            products = data if isinstance(data, list) else data.get('results', [])
            low_stock = [p for p in products if isinstance(p, dict) and p.get('stock', 0) < threshold]
            return Response({'threshold': threshold, 'low_stock_count': len(low_stock), 'products': low_stock})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
