from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class CheckUserType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_type = 'regular'
        
        if user.is_superuser:
            user_type = 'superuser'
        
        return Response({'user_type': user_type})