from api.User.model import CustomUser
from api.User.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet

class UserViewset(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer