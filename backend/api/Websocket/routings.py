from django.urls import re_path
from api.Websocket.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/user_(?P<user_id>\d+)/$', NotificationConsumer.as_asgi()),
]
