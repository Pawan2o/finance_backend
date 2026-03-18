from rest_framework import serializers
from .model import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'action_display', 'module', 'object_id', 'changes', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class AuditLogListSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'action_display', 'module', 'object_id', 'changes', 'timestamp']