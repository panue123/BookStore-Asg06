from django.urls import path, re_path
from .views import index, api_proxy, health, metrics

urlpatterns = [
    path('', index, name='index'),
    path('health/', health, name='health'),
    path('metrics/', metrics, name='metrics'),
    re_path(r'^api/proxy/(?P<path>.*)$', api_proxy, name='api_proxy'),
    re_path(r'^api/(?P<path>.*)$', api_proxy, name='api_proxy_legacy'),
]
