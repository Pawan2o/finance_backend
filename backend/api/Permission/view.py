from django.contrib.auth.models import Permission, ContentType
from api.Permission.serializer import PermissionSerializer
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class PermissionViewset(ModelViewSet):
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'codename']
    filterset_fields = ['content_type']
    ordering_fields = ['name', 'codename']
    ordering = ['name']
    
    def get_queryset(self):
        exclude_content_types = ContentType.objects.filter(
            model__in=['session', 'blacklistedtoken', 'outstandingtoken', 'logentry', 'contenttype', 'permission']
        )
        return Permission.objects.exclude(content_type__in=exclude_content_types)