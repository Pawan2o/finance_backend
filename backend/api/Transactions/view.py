from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .model import Transaction
from .serializer import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related(
            "type",
            "category",
            "payment_method"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Soft delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()

        return Response(
            {"message": "Transaction deleted successfully"},
            status=status.HTTP_200_OK
        )