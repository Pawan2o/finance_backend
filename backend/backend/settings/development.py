from .base import *
import os
from dotenv import load_dotenv

load_dotenv(override=True)

USER = os.getenv("USER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB = os.getenv("DB")
PASS = os.getenv("PASS")

DEBUG = True

ALLOWED_HOSTS = [
    "*"
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://finance-backend-0bbu.onrender.com",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': '5432',
    }
}

BASE_URL = os.getenv("BASE_URL")

STATIC_ROOT = BASE_DIR / "staticfiles"

CORS_ALLOW_CREDENTIALS = True