from rest_framework import viewsets
from .model import PaymentMethod
from .serializer import PaymentMethodSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer