import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


class SendEmailOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Authenticate user (check password)
        authenticated_user = authenticate(username=user.username, password=password)
        if not authenticated_user:
            return Response({"error": "Invalid password"}, status=401)

        # Generate 6 digit OTP
        otp = random.randint(100000, 999999)

        # Store OTP in cache for 5 minutes
        cache.set(f"email_otp_{email}", otp, timeout=300)

        # Send OTP to email
        send_mail(
            subject="Your Login OTP",
            message=f"Your OTP is {otp}",
            from_email=None,
            recipient_list=[email],
        )

        return Response({"message": "OTP sent successfully"})
    

class VerifyEmailOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"error": "Email and OTP required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check OTP from cache
        stored_otp = cache.get(f"email_otp_{email}")

        if not stored_otp:
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(stored_otp) != str(otp):
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP verified successfully
        cache.delete(f"email_otp_{email}")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Get user role dynamically
        role_name = 'user'
        if user.is_superuser:
            role_name = 'admin'
        elif user.groups.exists():
            role_name = user.groups.first().name

        return Response({
            "message": "OTP verified successfully",
            "access": access_token,
            "refresh": refresh_token,
            "role": {"name": role_name}
        }, status=status.HTTP_200_OK)