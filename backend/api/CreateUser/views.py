from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.User.serializers import UserSerializer
from rest_framework.permissions import AllowAny

class CreateUserAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Check if 'groups' is in the request data; if not, set it to an empty list
        data = request.data.copy()  # Make a mutable copy of request data
        if 'groups' not in data:
            data['groups'] = []

        # Pass the updated data to the serializer
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

