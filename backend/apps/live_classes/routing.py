"""WebSocket routing for live classes."""
from django.urls import re_path
from .consumers import LiveClassConsumer

websocket_urlpatterns = [
    re_path(r'ws/live-class/(?P<room_id>[^/]+)/$', LiveClassConsumer.as_asgi()),
]
