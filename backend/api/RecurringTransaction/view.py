from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from api.RecurringTransaction.model import RecurringTransaction
from api.RecurringTransaction.serializer import RecurringTransactionSerializer
from api.response_formatter import APIResponse


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["type", "category", "payment_method", "frequency", "is_active"]
    search_fields = ["description"]
    ordering_fields = ["amount", "start_date", "next_run_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return RecurringTransaction.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related(
            "type",
            "category",
            "payment_method",
            "user"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])
        return APIResponse.deleted("Recurring transaction deleted successfully")

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Toggle is_active status"""
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return APIResponse.success(
            f"Recurring transaction {'activated' if instance.is_active else 'deactivated'} successfully",
            {"is_active": instance.is_active}
        )

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active recurring transactions"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success("Active recurring transactions", serializer.data)