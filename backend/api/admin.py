from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.User.model import CustomUser

admin.site.register(CustomUser, UserAdmin)
