from api.User.model import CustomUser
from api.User.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import Http404


class UserViewset(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff', 'date_joined']
    ordering_fields = ['username', 'date_joined']
    ordering = ['-date_joined']

    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate user"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({
            'message': 'User deactivated successfully',
            'action': 'soft_delete'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='permanent-delete')
    def permanent_delete(self, request, pk=None):
        """Hard delete - permanently remove user from database"""
        try:
            instance = self.get_object()
            username = instance.username
            instance.delete()  # This will trigger post_delete signal
            return Response({
                'message': f'User {username} permanently deleted from database',
                'action': 'hard_delete'
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to delete user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)