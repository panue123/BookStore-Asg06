from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AddressViewSet,
    CustomerViewSet,
    health,
    JobViewSet,
    ManagerViewSet,
    StaffViewSet,
    UserAccountViewSet,
)
from .manager_views import (
    dashboard,
    sales_report,
    inventory_report,
    shipping_report,
    update_inventory,
    inventory_logs,
)

router = DefaultRouter()
router.register(r'users', UserAccountViewSet, basename='users')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'manager', ManagerViewSet, basename='manager')
router.register(r'addresses', AddressViewSet, basename='addresses')
router.register(r'jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health),
    # Manager dashboard & reports — dùng prefix mgr/ để tránh conflict với ManagerViewSet router
    path('mgr/dashboard/',         dashboard),
    path('mgr/sales_report/',      sales_report),
    path('mgr/inventory_report/',  inventory_report),
    path('mgr/shipping_report/',   shipping_report),
    path('mgr/update_inventory/',  update_inventory),
    path('mgr/inventory_logs/',    inventory_logs),
]
