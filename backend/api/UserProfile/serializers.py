from rest_framework import serializers
from api.User.model import CustomUser
from api.UserProfile.model import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    
    date_of_birth = serializers.DateField(format="%d/%m/%Y",input_formats=["%d/%m/%Y"], required=False, allow_null=True)
    class Meta:
        model = UserProfile
        fields = ['uuid', 'contact_no', 'date_of_birth']
        read_only_fields = ['uuid']