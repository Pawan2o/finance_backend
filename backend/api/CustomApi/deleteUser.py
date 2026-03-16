from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.User.model import CustomUser


class DeleteUserAPI(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request, user_id):

        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()

            return Response(
                {
                    "status": True,
                    "message": "User deleted successfully"
                },
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )