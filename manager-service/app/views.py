import requests
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Manager, InventoryLog, SalesReport
from .serializers import ManagerSerializer, InventoryLogSerializer, SalesReportSerializer


class ManagerViewSet(viewsets.ModelViewSet):
    """Manager Service - Dashboard and management functions"""
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    @action(detail=False, methods=['post'])
    def dashboard(self, request):
        """Get manager dashboard with key metrics"""
        try:
            # Get sales data from Order Service
            orders_resp = requests.get('http://order-service:8000/api/orders/')
            total_orders = 0
            total_revenue = 0
            
            if orders_resp.status_code == 200:
                orders = orders_resp.json()
                if isinstance(orders, list):
                    total_orders = len(orders)
                    total_revenue = sum(float(o.get('total_amount', 0)) for o in orders if o)
            
            # Get inventory summary
            books_resp = requests.get('http://book-service:8000/api/books/')
            total_books = 0
            low_stock_books = []
            
            if books_resp.status_code == 200:
                books = books_resp.json()
                if isinstance(books, list):
                    total_books = len(books)
                    for book in books:
                        if isinstance(book, dict) and book.get('stock', 0) < 10:
                            low_stock_books.append({
                                'id': book.get('id'),
                                'title': book.get('title'),
                                'stock': book.get('stock')
                            })
            
            # Get customer count
            customers_resp = requests.get('http://customer-service:8000/api/customers/')
            total_customers = 0
            if customers_resp.status_code == 200:
                customers = customers_resp.json()
                total_customers = len(customers) if isinstance(customers, list) else 0
            
            return Response({
                'dashboard': {
                    'total_orders': total_orders,
                    'total_revenue': float(total_revenue),
                    'total_books': total_books,
                    'total_customers': total_customers,
                    'low_stock_books': low_stock_books,
                    'timestamp': datetime.now().isoformat()
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_inventory(self, request):
        """Update book inventory"""
        book_id = request.data.get('book_id')
        new_stock = request.data.get('new_stock')
        reason = request.data.get('reason', 'Manual adjustment')
        manager_id = request.data.get('manager_id')
        
        if not book_id or new_stock is None:
            return Response({'error': 'book_id and new_stock are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get current book stock
            book_resp = requests.get(f'http://book-service:8000/api/books/{book_id}/')
            if book_resp.status_code != 200:
                return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
            
            book_data = book_resp.json()
            previous_stock = book_data.get('stock', 0)
            
            # Update book stock
            update_resp = requests.patch(
                f'http://book-service:8000/api/books/{book_id}/update_stock/',
                data={'stock': new_stock}
            )
            
            if update_resp.status_code == 200:
                # Log the change
                manager = None
                if manager_id:
                    try:
                        manager = Manager.objects.get(id=manager_id)
                    except Manager.DoesNotExist:
                        pass
                
                log = InventoryLog.objects.create(
                    book_id=book_id,
                    book_title=book_data.get('title'),
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    change_amount=new_stock - previous_stock,
                    reason=reason,
                    created_by=manager
                )
                
                return Response({
                    'message': 'Inventory updated successfully',
                    'log': InventoryLogSerializer(log).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to update book stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def inventory_logs(self, request):
        """Get inventory change logs"""
        limit = int(request.query_params.get('limit', 20))
        
        logs = InventoryLog.objects.all().order_by('-created_at')[:limit]
        serializer = InventoryLogSerializer(logs, many=True)
        
        return Response({
            'count': len(logs),
            'logs': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        """Generate sales report for a period"""
        period = request.query_params.get('period', 'daily')  # daily, weekly, monthly
        
        try:
            # Get orders from Order Service
            orders_resp = requests.get('http://order-service:8000/api/orders/')
            if orders_resp.status_code != 200:
                return Response({'error': 'Failed to fetch orders'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            orders = orders_resp.json()
            if not isinstance(orders, list):
                orders = []
            
            # Calculate metrics
            total_orders = len(orders)
            total_revenue = sum(float(o.get('total_amount', 0)) for o in orders if o)
            
            # Get top selling book
            top_book_id = None
            if orders:
                top_book_id = orders[0].get('id')
            
            now = datetime.now()
            report = SalesReport.objects.create(
                period=period,
                total_orders=total_orders,
                total_revenue=total_revenue,
                total_items_sold=sum(1 for o in orders),
                top_book_id=top_book_id,
                report_date=now.date()
            )
            
            return Response({
                'report': SalesReportSerializer(report).data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        """Get books with low stock"""
        threshold = int(request.query_params.get('threshold', 10))
        
        try:
            books_resp = requests.get('http://book-service:8000/api/books/')
            if books_resp.status_code != 200:
                return Response({'error': 'Failed to fetch books'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            books = books_resp.json()
            if not isinstance(books, list):
                books = []
            
            low_stock = [b for b in books if isinstance(b, dict) and b.get('stock', 0) < threshold]
            
            return Response({
                'threshold': threshold,
                'low_stock_count': len(low_stock),
                'books': low_stock
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get customer stats
        try:
            customers = requests.get('http://customer-service:8000/api/customers/').json()
            dashboard_data['customers'] = {
                'total': len(customers),
                'count': len(customers)
            }
        except Exception as e:
            dashboard_data['errors'].append(f'Customer Service: {str(e)}')
        
        # Get book stats
        try:
            books = requests.get('http://book-service:8000/api/books/').json()
            dashboard_data['books'] = {
                'total': len(books),
                'count': len(books),
                'categories': len(set(b.get('category', '') for b in books))
            }
        except Exception as e:
            dashboard_data['errors'].append(f'Book Service: {str(e)}')
        
        # Get order stats
        try:
            orders = requests.get('http://order-service:8000/api/orders/').json()
            dashboard_data['orders'] = {
                'total': len(orders),
                'count': len(orders),
                'total_revenue': sum(float(o.get('total_amount', 0)) for o in orders if isinstance(orders, list))
            }
        except Exception as e:
            dashboard_data['errors'].append(f'Order Service: {str(e)}')
        
        return Response(dashboard_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        """Get sales report"""
        try:
            orders = requests.get('http://order-service:8000/api/orders/').json()
            
            if not isinstance(orders, list):
                return Response({'error': 'Invalid order data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            paid_orders = [o for o in orders if o.get('status') == 'paid']
            total_sales = sum(float(o.get('total_amount', 0)) for o in paid_orders)
            
            return Response({
                'total_orders': len(orders),
                'paid_orders': len(paid_orders),
                'total_sales': total_sales,
                'average_order_value': total_sales / len(paid_orders) if paid_orders else 0
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        """Get inventory report"""
        try:
            books = requests.get('http://book-service:8000/api/books/').json()
            
            if not isinstance(books, list):
                return Response({'error': 'Invalid book data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            total_books = len(books)
            books_in_stock = len([b for b in books if b.get('stock', 0) > 0])
            out_of_stock = len([b for b in books if b.get('stock', 0) == 0])
            total_inventory_value = sum(float(b.get('price', 0)) * b.get('stock', 0) for b in books)
            
            return Response({
                'total_books': total_books,
                'in_stock': books_in_stock,
                'out_of_stock': out_of_stock,
                'total_inventory_value': total_inventory_value
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['get'])
    def shipping_report(self, request):
        """Get shipping report"""
        try:
            shipments = requests.get('http://ship-service:8000/api/shipments/').json()
            
            if not isinstance(shipments, list):
                return Response({'error': 'Invalid shipment data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            shipped = len([s for s in shipments if s.get('status') == 'shipped'])
            delivered = len([s for s in shipments if s.get('status') == 'delivered'])
            pending = len([s for s in shipments if s.get('status') in ['pending', 'processing']])
            
            return Response({
                'total_shipments': len(shipments),
                'shipped': shipped,
                'delivered': delivered,
                'pending': pending
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
