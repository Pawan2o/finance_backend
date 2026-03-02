# api/Category/view.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone

from api.Category.model import Category
from api.Category.serializer import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.filter(deleted_at__isnull=True)

        # Filter by type ( ?type=1 )
        type_id = self.request.query_params.get("type")
        if type_id:
            queryset = queryset.filter(type_id=type_id)

        return queryset

    # Soft delete instead of hard delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()

        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_200_OK,
        )