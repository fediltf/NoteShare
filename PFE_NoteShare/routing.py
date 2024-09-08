from django.urls import path, include, re_path
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<id>\d+)/$', ChatConsumer.as_asgi()),
]