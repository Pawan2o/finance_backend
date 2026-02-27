import os
from dotenv import load_dotenv
load_dotenv(override=True)
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.Websocket.routings

ENV = os.getenv("ENV")

if ENV == "local":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
elif ENV == "development":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')
elif ENV == "stage":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.stage')
elif ENV == "production":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.production')


# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            api.Websocket.routings.websocket_urlpatterns
        )
    ),
})
