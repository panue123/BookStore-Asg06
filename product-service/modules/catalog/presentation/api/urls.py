from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.product_view import ProductViewSet
from .views.category_view import CategoryViewSet

router = DefaultRouter()
router.register('products',   ProductViewSet,  basename='product')
router.register('categories', CategoryViewSet, basename='category')


@api_view(['GET'])
def health(request):
    from modules.catalog.infrastructure.models.product_model import ProductModel
    from modules.catalog.infrastructure.models.category_model import CategoryModel
    return Response({
        "service": "product-service",
        "status": "healthy",
        "products": ProductModel.objects.filter(is_active=True).count(),
        "categories": CategoryModel.objects.count(),
    })


urlpatterns = [
    path('', include(router.urls)),
    path('health/', health, name='health'),
]
