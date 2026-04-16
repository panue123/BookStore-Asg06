from django.shortcuts import render
import requests

PRODUCT_SERVICE_URL = "http://product-service:8000/api"

def book_list(request):
    r = requests.get(f"{PRODUCT_SERVICE_URL}/products/")
    data = r.json()
    items = data.get("results", data) if isinstance(data, dict) else data
    books = [
        {
            **b,
            "title": b.get("title") or b.get("name") or "",
            "author": b.get("author") or (b.get("attributes") or {}).get("author") or "",
        }
        for b in (items or [])
    ]
    return render(request, "books.html", {"books": books})

CART_SERVICE_URL = "http://cart-service:8000"

def view_cart(request, customer_id):
    r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
    return render(request, "cart.html", {"items": r.json()})