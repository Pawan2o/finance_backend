from django.contrib.auth.models import Group
from api.Role.serializer import RoleSerializer
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class RoleViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']