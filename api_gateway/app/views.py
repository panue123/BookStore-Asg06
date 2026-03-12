import json
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    """Serve the single-page application frontend."""
    # Keep the gateway UI self-contained. It calls APIs via /api/proxy/...
    return render(request, 'home.html')

@csrf_exempt
def api_proxy(request, path):
    """Proxy requests to backend microservices."""
    if not path:
        return JsonResponse({'error': 'Empty path'}, status=400)
        
    parts = path.split('/')
    service_alias = parts[0]
    
    # Map of API endpoints to their respective microservices
    service_map = {
        # Customer Service
        'customers': 'customer-service',
        'jobs': 'customer-service',
        'addresses': 'customer-service',
        
        # Book Service
        'books': 'book-service',
        'publishers': 'book-service',
        
        # Cart Service
        'carts': 'cart-service',
        
        # Order Service
        'orders': 'order-service',
        
        # Payment Service
        'payments': 'pay-service',
        
        # Shipping Service
        'shipments': 'ship-service',
        
        # Staff Service
        'staff': 'staff-service',
        
        # Comment/Rating Service
        'comments': 'comment-rate-service',
        
        # Catalog Service
        'catalog': 'catalog-service',
        
        # Manager Service
        'manager': 'manager-service',
        
        # Recommender Service
        'recommendations': 'recommender-ai-service',
    }
    
    if service_alias not in service_map:
        return JsonResponse({'error': f'Gateway route not found for {service_alias}'}, status=404)
        
    target_service = service_map[service_alias]
    target_url = f"http://{target_service}:8000/api/{path}"
    
    try:
        method = request.method
        headers = {}
        
        # Copy relevant headers
        if request.content_type:
            headers['Content-Type'] = request.content_type
        
        # Forward authorization header if present
        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        
        # Determine payload
        data = request.body if request.body else None
        
        resp = requests.request(
            method=method,
            url=target_url,
            params=request.GET,
            data=data,
            headers=headers,
            timeout=30
        )
        
        return HttpResponse(
            content=resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Request timeout - upstream service is slow'}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Upstream service unavailable: {str(e)}'}, status=503)
