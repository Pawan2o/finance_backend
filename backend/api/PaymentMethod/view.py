from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .model import PaymentMethod
from .serializer import PaymentMethodSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['payment_method']
    filterset_fields = ['is_active', 'created_at']
    ordering_fields = ['payment_method', 'created_at']
    ordering = ['-created_at']