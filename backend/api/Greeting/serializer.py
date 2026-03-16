from rest_framework import serializers
from .model import Greeting


class GreetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Greeting
        fields = ['id', 'greeting_type', 'message']