from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

    @action(detail=False, methods=['post'], url_path='batch_create')
    def batch_create(self, request):
        items = request.data if isinstance(request.data, list) else [request.data]
        created, skipped = [], 0

        for item in items:
            fingerprint = item.get('fingerprint')
            if fingerprint and Transaction.objects.filter(
                user=request.user, fingerprint=fingerprint
            ).exists():
                skipped += 1
                continue

            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                transaction = serializer.save(user=request.user)
                created.append(str(transaction.id))
            else:
                return Response(
                    {'errors': serializer.errors, 'item': item},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Notify via WebSocket
        if created:
            channel_layer = get_channel_layer()
            group_name = f'user_{request.user.id}'
            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'notify',
                'message': {'event': 'transactions_synced', 'count': len(created)}
            })

        return Response({'created': len(created), 'skipped': skipped, 'ids': created}, status=status.HTTP_201_CREATED)