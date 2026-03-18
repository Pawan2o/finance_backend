from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .model import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer
from api.response_formatter import APIResponse

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering = ['-timestamp']
    search_fields = ['user__username', 'module', 'action', 'object_id']
    filterset_fields = ['action', 'module', 'user']
    
    def get_queryset(self):
        # Only superusers can see all logs, regular users see only their own
        if self.request.user.is_superuser:
            queryset = AuditLog.objects.all().select_related('user')
        else:
            queryset = AuditLog.objects.filter(user=self.request.user).select_related('user')
        
        # Filter out admin if requested
        exclude_admin = self.request.query_params.get('exclude_admin', 'false').lower() == 'true'
        if exclude_admin:
            queryset = queryset.exclude(user__username='admin')
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AuditLogListSerializer
        return AuditLogSerializer
    

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success("Audit logs retrieved successfully", serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success("Audit log retrieved successfully", serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit log statistics"""
        queryset = self.get_queryset()
        
        # Basic stats
        total_logs = queryset.count()
        today_logs = queryset.filter(timestamp__date=timezone.now().date()).count()
        week_logs = queryset.filter(timestamp__gte=timezone.now() - timedelta(days=7)).count()
        
        # Action breakdown
        action_stats = queryset.values('action').annotate(count=Count('id')).order_by('-count')
        
        # Module breakdown
        module_stats = queryset.values('module').annotate(count=Count('id')).order_by('-count')
        
        # Recent activity (last 24 hours)
        recent_activity = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).values('action', 'module').annotate(count=Count('id'))
        
        stats_data = {
            'summary': {
                'total_logs': total_logs,
                'today_logs': today_logs,
                'week_logs': week_logs,
                'active_users': queryset.values('user').distinct().count()
            },
            'actions': list(action_stats),
            'modules': list(module_stats),
            'recent_activity': list(recent_activity)
        }
        
        return APIResponse.success("Audit log statistics retrieved successfully", stats_data)
    
    @action(detail=False, methods=['post'])
    def bulk_delete_admin_logs(self, request):
        """Delete old admin logs (older than specified days)"""
        if not request.user.is_superuser:
            return APIResponse.error("Only superusers can delete audit logs", status_code=403)
            
        days = request.data.get('days', 30)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        deleted_count = AuditLog.objects.filter(
            user__username='admin',
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        return APIResponse.success(f"Deleted {deleted_count} old admin logs", {'deleted_count': deleted_count})
    
    @action(detail=False, methods=['get'])
    def admin_summary(self, request):
        """Get summarized admin activities instead of individual entries"""
        # Get base queryset
        if self.request.user.is_superuser:
            queryset = AuditLog.objects.all().select_related('user')
        else:
            queryset = AuditLog.objects.filter(user=self.request.user).select_related('user')
        
        queryset = queryset.filter(user__username='admin')
        
        # Group by date, module, and action
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        summary = queryset.annotate(
            date=TruncDate('timestamp')
        ).values('date', 'module', 'action').annotate(
            count=Count('id')
        ).order_by('-date', 'module', 'action')
        
        return APIResponse.success("Admin activity summary retrieved", list(summary))
    
    @action(detail=False, methods=['get'])
    def debug_ip(self, request):
        """Debug endpoint - IP tracking disabled"""
        if not request.user.is_superuser:
            return APIResponse.error("Only superusers can access debug info", status_code=403)
            
        return APIResponse.success("IP tracking has been disabled", {"message": "IP address logging is no longer active"})
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get timeline of activities for the last 30 days"""
        queryset = self.get_queryset()
        
        # Get activities for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        timeline_data = []
        
        for i in range(30):
            date = (thirty_days_ago + timedelta(days=i)).date()
            day_logs = queryset.filter(timestamp__date=date)
            
            timeline_data.append({
                'date': date.isoformat(),
                'total_activities': day_logs.count(),
                'actions': dict(day_logs.values('action').annotate(count=Count('id')).values_list('action', 'count')),
                'modules': dict(day_logs.values('module').annotate(count=Count('id')).values_list('module', 'count'))
            })
        
        return APIResponse.success("Activity timeline retrieved successfully", timeline_data)