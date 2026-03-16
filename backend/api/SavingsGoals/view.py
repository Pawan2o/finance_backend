from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum, Q, Count, Avg
from django.utils import timezone
from decimal import Decimal

from .model import SavingsGoals
from .serializer import SavingsGoalsSerializer, SavingsGoalsDetailSerializer

class SavingsGoalsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status', 'target_category', 'deadline']
    ordering_fields = ['created_at', 'deadline', 'target_amount', 'goal_name']
    ordering = ['-created_at']
    search_fields = ['goal_name', 'description']
    
    def get_queryset(self):
        return SavingsGoals.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related('user', 'target_category')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SavingsGoalsDetailSerializer
        return SavingsGoalsSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
    
    @action(detail=False, methods=['get'])
    def active_goals(self, request):
        """Get all active savings goals"""
        goals = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed_goals(self, request):
        """Get all completed savings goals"""
        goals = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get savings goals summary"""
        goals = self.get_queryset()
        
        # Calculate totals
        total_target = sum(goal.target_amount for goal in goals)
        total_saved = sum(goal.saved_amount for goal in goals)
        
        summary_data = {
            'total_goals': goals.count(),
            'active_goals': goals.filter(status='active').count(),
            'completed_goals': goals.filter(status='completed').count(),
            'paused_goals': goals.filter(status='paused').count(),
            'cancelled_goals': goals.filter(status='cancelled').count(),
            'total_target_amount': float(total_target),
            'total_saved_amount': float(total_saved),
        }
        
        # Calculate overall progress
        if total_target > 0:
            summary_data['overall_progress'] = float((total_saved / total_target) * 100)
        else:
            summary_data['overall_progress'] = 0
            
        return Response(summary_data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get transactions contributing to this goal"""
        goal = self.get_object()
        transactions = goal.get_related_transactions()
        
        # Paginate transactions
        page = self.paginate_queryset(transactions)
        if page is not None:
            from api.Transactions.serializer import TransactionSerializer
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        from api.Transactions.serializer import TransactionSerializer
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update goal status"""
        goal = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(SavingsGoals.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        goal.status = new_status
        goal.save(update_fields=['status', 'updated_at'])
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def progress_report(self, request):
        """Get detailed progress report"""
        goals = self.get_queryset().filter(status='active')
        
        report_data = []
        for goal in goals:
            goal_data = {
                'id': str(goal.id),
                'goal_name': goal.goal_name,
                'target_amount': float(goal.target_amount),
                'saved_amount': float(goal.saved_amount),
                'progress_percentage': goal.progress_percentage,
                'remaining_amount': float(goal.remaining_amount),
                'deadline': goal.deadline,
                'days_remaining': (goal.deadline - timezone.now().date()).days,
                'category': goal.target_category.name if goal.target_category else None,
            }
            report_data.append(goal_data)
        
        return Response({
            'goals': report_data,
            'total_goals': len(report_data),
            'average_progress': sum(g['progress_percentage'] for g in report_data) / len(report_data) if report_data else 0
        })