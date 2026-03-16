from rest_framework import viewsets
from rest_framework.response import Response
from datetime import datetime
from .model import Greeting
from .serializer import GreetingSerializer
from rest_framework.decorators import action


class GreetingViewSet(viewsets.ModelViewSet):

    serializer_class = GreetingSerializer
    queryset = Greeting.objects.all()

    @action(detail=False, methods=['get'])
    def current_greeting(self, request):

        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            greeting_type = "morning"
        elif 12 <= current_hour < 17:
            greeting_type = "afternoon"
        elif 17 <= current_hour < 21:
            greeting_type = "evening"
        else:
            greeting_type = "night"

        greeting = Greeting.objects.filter(
            greeting_type=greeting_type
        ).first()

        if not greeting:
            return Response({
                "current_time": datetime.now().strftime("%H:%M:%S"),
                "greeting": None,
                "message": f"No greeting found for {greeting_type}"
            })

        serializer = GreetingSerializer(greeting)

        return Response({
            "current_time": datetime.now().strftime("%H:%M:%S"),
            "greeting": serializer.data
        })