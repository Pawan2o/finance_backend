from .base import *
import os
from dotenv import load_dotenv
load_dotenv(override=True)

USER = os.getenv("USER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB = os.getenv("DB")
PASS = os.getenv("PASS")

DEBUG = False
ALLOWED_HOSTS = [ "https://placeholder-stage.humbingo.in"]

CORS_ALLOWED_ORIGINS = [ 
    "https://placeholder-stage.humbingo.in",
]

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': DB,
         'HOST': HOST,
         'PORT': PORT,
         'USER':USER,
         'PASSWORD': PASS
     }
}

BASE_URL = os.getenv("BASE_URL")