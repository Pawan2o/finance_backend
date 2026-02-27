from api.permissions import CustomPermission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ChangeMyPasswordView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)