from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, PublisherViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'publishers', PublisherViewSet, basename='publisher')

urlpatterns = [
    path('', include(router.urls)),
]