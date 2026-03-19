from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.core.cache import cache
import logging
from .model import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer
from api.response_formatter import APIResponse
from api.permissions import IsSuperUser

logger = logging.getLogger(__name__)


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    permission_classes = [IsAuthenticated, IsSuperUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'module', 'user']
    search_fields = ['module', 'object_id', 'user__username']
    ordering_fields = ['timestamp', 'action', 'module']
    ordering = ['-timestamp']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuditLogListSerializer
        return AuditLogSerializer

    def get_queryset(self):
        """Optimized queryset with proper filtering and caching"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                queryset = queryset.filter(timestamp__date__gte=start_date)
            except ValueError:
                logger.warning(f"Invalid start_date format: {start_date}")
                
        if end_date:
            try:
                queryset = queryset.filter(timestamp__date__lte=end_date)
            except ValueError:
                logger.warning(f"Invalid end_date format: {end_date}")
        
        # Hide admin logs if requested
        hide_admin = self.request.query_params.get('hide_admin', 'false').lower() == 'true'
        if hide_admin:
            queryset = queryset.exclude(user__is_superuser=True)
        
        # Default to last 30 days if no date filter provided
        if not start_date and not end_date:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(timestamp__gte=thirty_days_ago)
            
        return queryset.select_related('user', 'created_by')

    @action(detail=False, methods=['delete'], url_path='cleanup')
    def cleanup_logs(self, request):
        """Clean up old audit logs with enhanced validation"""
        try:
            days = request.query_params.get('days', '30')
            dry_run = request.query_params.get('dry_run', 'false').lower() == 'true'
            
            # Validate days parameter
            try:
                days = int(days)
            except ValueError:
                return APIResponse.error(
                    message="Days parameter must be a valid integer",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Restrict allowed values for safety
            allowed_days = [0, 1, 7, 30, 90, 180, 365]
            if days not in allowed_days:
                return APIResponse.error(
                    message=f"Days must be one of: {allowed_days}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate logs to delete
            if days == 0:
                logs_to_delete = AuditLog.objects.all()
                cutoff_date = None
                warning_msg = "This will delete ALL audit logs permanently!"
            else:
                cutoff_date = timezone.now() - timedelta(days=days)
                logs_to_delete = AuditLog.objects.filter(timestamp__lt=cutoff_date)
                warning_msg = f"This will delete logs older than {days} days"
            
            count = logs_to_delete.count()
            total_logs = AuditLog.objects.count()
            
            logger.info(f"Cleanup request: days={days}, dry_run={dry_run}, count={count}")
            
            if dry_run:
                return APIResponse.success(
                    data={
                        'count_to_delete': count,
                        'cutoff_date': cutoff_date.isoformat() if cutoff_date else 'ALL',
                        'days': days,
                        'dry_run': True,
                        'total_logs': total_logs,
                        'remaining_after_cleanup': total_logs - count,
                        'warning': warning_msg
                    },
                    message=f"Dry run: Would delete {count} audit logs {'(ALL LOGS)' if days == 0 else f'older than {days} days'}"
                )
            
            if count == 0:
                return APIResponse.success(
                    data={
                        'deleted_count': 0, 
                        'days': days,
                        'total_logs': total_logs,
                        'cutoff_date': cutoff_date.isoformat() if cutoff_date else 'ALL'
                    },
                    message=f"No audit logs found {'to delete' if days == 0 else f'older than {days} days'}"
                )
            
            # Perform deletion in batches for large datasets
            batch_size = 1000
            deleted_total = 0
            
            while True:
                batch_ids = list(logs_to_delete.values_list('id', flat=True)[:batch_size])
                if not batch_ids:
                    break
                    
                deleted_count, _ = AuditLog.objects.filter(id__in=batch_ids).delete()
                deleted_total += deleted_count
                
                if deleted_count < batch_size:
                    break
            
            logger.info(f"Cleanup completed: deleted {deleted_total} logs")
            
            return APIResponse.success(
                data={
                    'deleted_count': deleted_total,
                    'days': days,
                    'cutoff_date': cutoff_date.isoformat() if cutoff_date else 'ALL',
                    'remaining_logs': AuditLog.objects.count()
                },
                message=f"Successfully deleted {deleted_total} audit logs {'(ALL LOGS CLEARED)' if days == 0 else f'older than {days} days'}"
            )
            
        except Exception as e:
            logger.error(f"Error in cleanup_logs: {str(e)}")
            return APIResponse.error(
                message="An error occurred during cleanup",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """Get comprehensive audit log statistics with caching"""
        try:
            # Try to get from cache first
            cache_key = 'audit_log_stats'
            cached_stats = cache.get(cache_key)
            
            if cached_stats:
                return APIResponse.success(
                    data=cached_stats,
                    message="Audit log statistics retrieved from cache"
                )
            
            now = timezone.now()
            
            # Basic counts
            total_logs = AuditLog.objects.count()
            
            # Time-based statistics
            time_stats = {
                'total_logs': total_logs,
                'logs_today': AuditLog.objects.filter(
                    timestamp__date=now.date()
                ).count(),
                'logs_7_days': AuditLog.objects.filter(
                    timestamp__gte=now - timedelta(days=7)
                ).count(),
                'logs_30_days': AuditLog.objects.filter(
                    timestamp__gte=now - timedelta(days=30)
                ).count(),
                'logs_90_days': AuditLog.objects.filter(
                    timestamp__gte=now - timedelta(days=90)
                ).count(),
            }
            
            # Action-based statistics
            action_stats = dict(
                AuditLog.objects.values('action').annotate(
                    count=Count('id')
                ).values_list('action', 'count')
            )
            
            # Module-based statistics
            module_stats = dict(
                AuditLog.objects.values('module').annotate(
                    count=Count('id')
                ).order_by('-count')[:10].values_list('module', 'count')
            )
            
            # User activity statistics
            user_stats = list(
                AuditLog.objects.filter(user__isnull=False)
                .values('user__username')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            stats = {
                **time_stats,
                'action_breakdown': action_stats,
                'top_modules': module_stats,
                'top_users': user_stats,
                'old_logs_30_days': AuditLog.objects.filter(
                    timestamp__lt=now - timedelta(days=30)
                ).count(),
                'old_logs_90_days': AuditLog.objects.filter(
                    timestamp__lt=now - timedelta(days=90)
                ).count(),
                'generated_at': now.isoformat()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)
            
            logger.info("Audit log statistics generated and cached")
            
            return APIResponse.success(
                data=stats,
                message="Audit log statistics retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in get_stats: {str(e)}")
            return APIResponse.error(
                message="An error occurred while retrieving statistics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='user-activity')
    def user_activity(self, request):
        """Get user-specific activity logs"""
        try:
            user_id = request.query_params.get('user_id')
            days = int(request.query_params.get('days', 7))
            
            if not user_id:
                return APIResponse.error(
                    message="user_id parameter is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = timezone.now() - timedelta(days=days)
            
            logs = AuditLog.objects.filter(
                user_id=user_id,
                timestamp__gte=start_date
            ).select_related('user').order_by('-timestamp')
            
            serializer = AuditLogListSerializer(logs, many=True)
            
            return APIResponse.success(
                data={
                    'logs': serializer.data,
                    'count': logs.count(),
                    'user_id': user_id,
                    'days': days
                },
                message=f"User activity for last {days} days retrieved successfully"
            )
            
        except ValueError:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in user_activity: {str(e)}")
            return APIResponse.error(
                message="An error occurred while retrieving user activity",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )