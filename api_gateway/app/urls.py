from django.urls import path, re_path
from .views import index, api_proxy

urlpatterns = [
    path('', index, name='index'),
    # Preferred client-facing gateway prefix (matches project docs)
    re_path(r'^api/proxy/(?P<path>.*)$', api_proxy, name='api_proxy'),
    # Backward-compatible route
    re_path(r'^api/(?P<path>.*)$', api_proxy, name='api_proxy_legacy'),
]
