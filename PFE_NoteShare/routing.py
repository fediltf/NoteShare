from django.urls import path, include
from PFE_NoteShare.consumer import ChatConsumer

# the empty string routes to ChatConsumer, which manages the chat functionality.
websocket_urlpatterns = [
    path("", ChatConsumer.as_asgi()),
    # path('ws/chat/admin/', ChatConsumer.as_asgi()),
]
