
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add user role to token (using Django Groups)
        user_groups = user.groups.all()
        
        if user_groups.exists():
            token['role'] = user_groups.first().name
            token['role_id'] = user_groups.first().id
        else:
            token['role'] = None
            token['role_id'] = None
        
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data