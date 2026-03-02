from rest_framework import serializers
from django.contrib.auth.models import User
from api.UserProfile.model import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['contact_no']