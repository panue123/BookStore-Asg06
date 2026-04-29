from django.urls import path

from .views import NotificationViewSet, health

notification_list = NotificationViewSet.as_view({'get': 'list', 'post': 'create'})
notification_detail = NotificationViewSet.as_view({'get': 'retrieve'})
notification_send = NotificationViewSet.as_view({'post': 'send'})

urlpatterns = [
    path('', notification_list),
    path('health/', health),
    path('<int:pk>/', notification_detail),
    path('<int:pk>/send/', notification_send),
]
