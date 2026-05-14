from .base import *
import os
from dotenv import load_dotenv
load_dotenv(override=True)

DEBUG = False
ALLOWED_HOSTS = ["finance-backend-0bbu.onrender.com"]

CORS_ALLOWED_ORIGINS = [
    "https://placeholder.humbingo.in",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT", "5432"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASS"),
    }
}

BASE_URL = os.getenv("BASE_URL")