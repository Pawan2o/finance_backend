from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .model import Transaction
from .serializer import TransactionSerializer
from api.response_formatter import APIResponse


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['description', 'amount']
    filterset_fields = ['type', 'category', 'payment_method', 'transaction_date', 'created_at']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date']

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return APIResponse.deleted("Transaction deleted successfully")