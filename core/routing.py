from django.urls import path
from .consumers import CheatingConsumer

websocket_urlpatterns = [
    path("ws/cheat/", CheatingConsumer.as_asgi()),
]