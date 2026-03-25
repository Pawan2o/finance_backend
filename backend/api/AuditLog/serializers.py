from rest_framework import serializers
from .model import AuditLog, IST_TIMEZONE
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class BaseAuditLogSerializer(serializers.ModelSerializer):
    """Base serializer with common fields and methods"""
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    
    def get_formatted_timestamp(self, obj):
        if not obj.timestamp:
            return None
        local_time = obj.timestamp.astimezone(IST_TIMEZONE)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

class AuditLogSerializer(BaseAuditLogSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_name', 'created_by_name', 'action', 'action_display', 
            'module', 'object_id', 'changes', 'timestamp', 'formatted_timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class AuditLogListSerializer(BaseAuditLogSerializer):
    changes_summary = serializers.SerializerMethodField()
    
    def get_changes_summary(self, obj):
        """Provide a summary of changes for list view"""
        if not obj.changes:
            return None
        
        if 'old' in obj.changes and 'new' in obj.changes:
            old_data = obj.changes.get('old', {})
            new_data = obj.changes.get('new', {})
            changed_fields = [
                key for key in new_data.keys() 
                if key in old_data and old_data[key] != new_data[key]
            ]
            return {'changed_fields': changed_fields, 'field_count': len(changed_fields)}
        
        return {'action': obj.action}
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_name', 'action', 'action_display', 'module', 
            'object_id', 'changes_summary', 'formatted_timestamp'
        ]