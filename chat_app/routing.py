from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from chat_app import consumer

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(
            [
                path("ws/chat/", consumer.FindConsumer.as_asgi()),
                path("ws/chat/<room_name>/", consumer.ChatConsumer.as_asgi()),
            ]
        )),
    }
)
