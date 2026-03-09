from rest_framework import viewsets
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from api.Category.model import Category
from api.Category.serializer import CategorySerializer
from api.response_formatter import APIResponse


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['type', 'created_at']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Category.objects.filter(deleted_at__isnull=True).select_related('type')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return APIResponse.deleted("Category deleted successfully")