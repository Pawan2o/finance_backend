from django.contrib.auth.models import User
from api.User.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet

class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer