# api/ForgetPassword/view.py

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from django.conf import settings
from django.core.cache import cache
import uuid

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]  # Allows access to any user, authenticated or not

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create a temporary token and store it in cache
            temp_token = str(uuid.uuid4())
            cache.set(temp_token, {'uid': uid, 'token': token}, timeout=3600)  # Expires in 1 hour

            reset_link = f"{settings.BASE_URL}/auth/pass-reset/{temp_token}/"

            subject = "Password Reset Request"
            message = (
                f"Hi {user.username},<br><br>"
                f"You requested a password reset. Click the link below to reset your password:<br>"
                f'<a href="{reset_link}">Reset Password</a><br><br>'
                "If you did not request this, please ignore this email.<br><br>"
                "Thank you."
            )
            email_message = EmailMessage(subject, message, to=[user.email])
            email_message.content_subtype = "html"
            email_message.send()

            return Response(
                {"detail": "A password reset link has been sent successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "No account found with this email address."},
                status=status.HTTP_400_BAD_REQUEST
            )

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, temp_token):
        # Get the actual uid and token from cache
        data = cache.get(temp_token)
        if not data:
            return Response({"detail": "Invalid or expired link"}, status=status.HTTP_400_BAD_REQUEST)

        uidb64 = data['uid']
        token = data['token']

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"detail": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                cache.delete(temp_token)  # Clean up the token after use
                return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
