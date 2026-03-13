from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum, Q, Count
from django.utils import timezone

from api.Budget.model import Budget
from api.Budget.serializer import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_fields = ["month", "year", "week", "category", "category__type"]
    ordering_fields = ["month", "year", "week", "amount", "created_at"]
    ordering = ["-year", "-month", "-week", "category__name"]
    search_fields = ["category__name"]

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related('category', 'category__type')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])

    @action(detail=False, methods=['get'])
    def current_month(self, request):
        """Get current month's budgets"""
        now = timezone.now()
        budgets = self.get_queryset().filter(month=now.month, year=now.year)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get budget summary for a specific month/year"""
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
            
            if not (1 <= month <= 12):
                return Response({'error': 'Month must be between 1-12'}, status=status.HTTP_400_BAD_REQUEST)
            if not (2000 <= year <= 2100):
                return Response({'error': 'Year must be between 2000-2100'}, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({'error': 'Invalid month or year'}, status=status.HTTP_400_BAD_REQUEST)
        
        budgets = self.get_queryset().filter(month=month, year=year)
        summary_data = budgets.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'month': month,
            'year': year,
            'total_budget': summary_data['total'] or 0,
            'budget_count': summary_data['count']
        })

    @action(detail=False, methods=['get'])
    def yearly_summary(self, request):
        """Get yearly budget summary"""
        try:
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            return Response({'error': 'Invalid year'}, status=status.HTTP_400_BAD_REQUEST)
            
        budgets = self.get_queryset().filter(year=year)
        return Response({
            'year': year,
            'total_budget': budgets.aggregate(total=Sum('amount'))['total'] or 0,
            'monthly_breakdown': list(budgets.values('month').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('month'))
        })