"""
Manager dashboard & report endpoints.
Aggregates data from order-service, product-service, ship-service.
"""
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

ORDER_SVC   = os.getenv('ORDER_SERVICE_URL',   'http://order-service:8000')
PRODUCT_SVC = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8000')
SHIP_SVC    = os.getenv('SHIP_SERVICE_URL',    'http://ship-service:8000')

TIMEOUT = 8


def _get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _get_list(url, params=None):
    data = _get(url, params)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return data.get('results') or data.get('orders') or data.get('shipments') or []


# ── Dashboard ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def dashboard(request):
    from .models import UserAccount, UserRole

    orders   = _get_list(f'{ORDER_SVC}/api/orders/')
    products = _get_list(f'{PRODUCT_SVC}/api/products/?page_size=500')

    total_orders    = len(orders)
    total_revenue   = sum(float(o.get('total_amount', 0) or 0) for o in orders if o.get('status') == 'paid')
    total_customers = UserAccount.objects.filter(role=UserRole.CUSTOMER).count()
    total_books     = len(products)

    low_stock = [
        {
            'id':     p.get('id'),
            'title':  p.get('name') or p.get('title') or '',
            'author': (p.get('attributes') or {}).get('brand') or (p.get('attributes') or {}).get('author') or '',
            'stock':  p.get('stock', 0),
        }
        for p in products
        if int(p.get('stock', 0) or 0) < 5
    ]
    low_stock.sort(key=lambda x: x['stock'])

    return JsonResponse({
        'dashboard': {
            'total_orders':    total_orders,
            'total_revenue':   total_revenue,
            'total_books':     total_books,
            'total_customers': total_customers,
            'low_stock_books': low_stock[:20],
        }
    })


# ── Sales report ──────────────────────────────────────────

def sales_report(request):
    orders = _get_list(f'{ORDER_SVC}/api/orders/')
    paid   = [o for o in orders if o.get('status') == 'paid']
    total_sales = sum(float(o.get('total_amount', 0) or 0) for o in paid)
    avg = round(total_sales / len(paid), 0) if paid else 0

    by_status = {}
    for o in orders:
        s = o.get('status', 'unknown')
        by_status[s] = by_status.get(s, 0) + 1

    return JsonResponse({
        'total_orders':        len(orders),
        'paid_orders':         len(paid),
        'total_sales':         total_sales,
        'average_order_value': avg,
        'by_status':           by_status,
    })


# ── Inventory report ──────────────────────────────────────

def inventory_report(request):
    products = _get_list(f'{PRODUCT_SVC}/api/products/?page_size=500')
    in_stock     = sum(1 for p in products if int(p.get('stock', 0) or 0) > 0)
    out_of_stock = sum(1 for p in products if int(p.get('stock', 0) or 0) == 0)
    total_value  = sum(
        float(p.get('price', 0) or 0) * int(p.get('stock', 0) or 0)
        for p in products
    )
    return JsonResponse({
        'total_books':           len(products),
        'in_stock':              in_stock,
        'out_of_stock':          out_of_stock,
        'total_inventory_value': round(total_value, 0),
    })


# ── Shipping report ───────────────────────────────────────

def shipping_report(request):
    ships = _get_list(f'{SHIP_SVC}/api/shipments/')
    by_status = {}
    for s in ships:
        st = s.get('status', 'unknown')
        by_status[st] = by_status.get(st, 0) + 1
    return JsonResponse({
        'total_shipments': len(ships),
        'pending':         by_status.get('pending', 0),
        'processing':      by_status.get('processing', 0),
        'shipped':         by_status.get('shipped', 0),
        'delivered':       by_status.get('delivered', 0),
        'cancelled':       by_status.get('cancelled', 0),
    })


# ── Inventory logs (in-memory from product stock changes) ─

_inventory_logs = []  # simple in-memory store


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def update_inventory(request):
    import json
    from django.utils import timezone

    if request.method == 'GET':
        return inventory_logs(request)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    book_id   = body.get('book_id')
    new_stock = body.get('new_stock')
    reason    = body.get('reason', 'Manual adjustment')

    if book_id is None or new_stock is None:
        return JsonResponse({'error': 'book_id and new_stock required'}, status=400)

    # Fetch current stock
    current = 0
    product_data = _get(f'{PRODUCT_SVC}/api/products/{book_id}/')
    if product_data:
        current = int(product_data.get('stock', 0) or 0)

    # PATCH product-service
    try:
        r = requests.patch(
            f'{PRODUCT_SVC}/api/products/{book_id}/',
            json={'stock': int(new_stock)},
            timeout=TIMEOUT,
        )
        if r.status_code not in (200, 201):
            return JsonResponse({'error': f'product-service error: {r.status_code}'}, status=502)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=503)

    log = {
        'book_id':        int(book_id),
        'book_title':     (product_data or {}).get('name') or (product_data or {}).get('title') or f'Product #{book_id}',
        'previous_stock': current,
        'new_stock':      int(new_stock),
        'change_amount':  int(new_stock) - current,
        'reason':         reason,
        'created_at':     timezone.now().isoformat(),
    }
    _inventory_logs.insert(0, log)
    if len(_inventory_logs) > 200:
        _inventory_logs.pop()

    return JsonResponse({'success': True, 'log': log})


def inventory_logs(request):
    limit = int(request.GET.get('limit', 50))
    return JsonResponse({'logs': _inventory_logs[:limit]})
