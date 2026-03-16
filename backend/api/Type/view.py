from rest_framework import viewsets
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from api.Type.model import Type
from api.Type.serializer import TypeSerializer
from api.response_formatter import APIResponse


class TypeViewSet(viewsets.ModelViewSet):
    serializer_class = TypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['created_at']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Type.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return APIResponse.deleted("Type deleted successfully")