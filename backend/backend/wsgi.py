import os
from dotenv import load_dotenv
load_dotenv(override=True)
from django.core.wsgi import get_wsgi_application
ENV = os.getenv("ENV")

if ENV == "local":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
elif ENV == "development":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')
elif ENV == "stage":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.stage')
elif ENV == "productions":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.production')

application = get_wsgi_application()
