from api.User.model import CustomUser
from api.User.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class UserViewset(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff', 'date_joined']
    ordering_fields = ['username', 'date_joined']
    ordering = ['-date_joined']