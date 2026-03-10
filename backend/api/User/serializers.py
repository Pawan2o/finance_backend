from rest_framework import serializers
from api.User.model import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from api.UserProfile.model import UserProfile


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False
    )

    contact_no = serializers.CharField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(
        format="%d/%m/%Y",
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        required=False,
        allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = ['id','username','password','email','first_name','last_name','groups','is_staff','is_active','is_superuser','date_joined','last_login','contact_no','date_of_birth']

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            'id': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True}
        }

    # Email validation
    def validate_email(self, value):
        user = self.instance
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk if user else None).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    # Response formatting
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        try:
            contact_no = instance.userprofile.contact_no
            date_of_birth = (
                instance.userprofile.date_of_birth.strftime("%d/%m/%Y")
                if instance.userprofile.date_of_birth else None
            )
        except UserProfile.DoesNotExist:
            contact_no = None
            date_of_birth = None

        return {
            **representation,
            'contact_no': contact_no,
            'date_of_birth': date_of_birth
        }

    # Create User
    def create(self, validated_data):

        groups_data = validated_data.pop('groups', [])
        contact_no = validated_data.pop('contact_no', None)
        date_of_birth = validated_data.pop('date_of_birth', None)

        # username = email if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data.get('email')

        # hash password
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        user = super().create(validated_data)

        # set groups
        if groups_data:
            user.groups.set(groups_data)
            self._update_user_permissions(user)

        # create profile
        UserProfile.objects.create(
            user=user,
            contact_no=contact_no,
            date_of_birth=date_of_birth
        )

        return user

    # Update User
    def update(self, instance, validated_data):

        groups_data = validated_data.pop('groups', None)
        contact_no = validated_data.pop('contact_no', None)
        date_of_birth = validated_data.pop('date_of_birth', None)

        # update password
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        # update user fields
        instance = super().update(instance, validated_data)

        # update groups only if provided
        if groups_data is not None:
            instance.groups.set(groups_data)
            self._update_user_permissions(instance)

        # update or create profile
        UserProfile.objects.update_or_create(
            user=instance,
            defaults={
                'contact_no': contact_no,
                'date_of_birth': date_of_birth
            }
        )

        return instance

    # update permissions from groups
    def _update_user_permissions(self, user):
        permissions = set()

        for group in user.groups.all():
            permissions.update(group.permissions.all())

        user.user_permissions.set(permissions)