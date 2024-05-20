from django.urls import path
from chat import consumers

websocket_urlpatterns = {
    path('<str:id>/', consumers.ChatConsumer.as_asgi()),
}
