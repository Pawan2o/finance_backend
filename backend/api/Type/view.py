from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone

from api.Type.model import Type
from api.Type.serializer import TypeSerializer


class TypeViewSet(viewsets.ModelViewSet):
    serializer_class = TypeSerializer

    def get_queryset(self):
        return Type.objects.filter(deleted_at__isnull=True)

    # Soft delete instead of hard delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()

        return Response(
            {"message": "Type deleted successfully"},
            status=status.HTTP_200_OK
        )