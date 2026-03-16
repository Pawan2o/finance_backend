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

    filterset_fields = ["month", "year", "week", "quarterly_start_date", "quarterly_end_date", "type", "budget_type"]
    ordering_fields = ["month", "year", "week", "quarterly_start_date", "amount", "created_at"]
    ordering = ["-year", "-month", "-week", "-quarterly_start_date", "type__name"]
    search_fields = ["type__name"]

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).select_related('type')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])

    @action(detail=False, methods=['get'])
    def budget_by_type(self, request):
        """Get budgets filtered by budget type"""
        budget_type = request.query_params.get('budget_type')
        if budget_type not in ['weekly', 'monthly', 'quarterly', 'yearly']:
            return Response({'error': 'Invalid budget type. Must be: weekly, monthly, quarterly, yearly'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        budgets = self.get_queryset().filter(budget_type=budget_type)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def quarterly_budgets(self, request):
        """Get quarterly budgets with date range filtering"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            queryset = self.get_queryset().filter(budget_type='quarterly')
            
            if start_date:
                queryset = queryset.filter(quarterly_start_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(quarterly_end_date__lte=end_date)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def current_quarter(self, request):
        """Get current quarter's budgets based on quarterly_start_date"""
        now = timezone.now().date()
        
        # Find quarterly budgets that include current date
        budgets = self.get_queryset().filter(
            budget_type='quarterly',
            quarterly_start_date__lte=now,
            quarterly_end_date__gte=now
        )
        
        serializer = self.get_serializer(budgets, many=True)
        return Response({
            'current_date': now,
            'budgets': serializer.data
        })

    @action(detail=False, methods=['get'])
    def quarterly_summary(self, request):
        """Get quarterly budget summary by date range"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date:
                return Response({'error': 'start_date is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.get_queryset().filter(
                budget_type='quarterly',
                quarterly_start_date__gte=start_date
            )
            
            if end_date:
                queryset = queryset.filter(quarterly_end_date__lte=end_date)
            
            summary_data = queryset.aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            return Response({
                'start_date': start_date,
                'end_date': end_date,
                'total_budget': summary_data['total'] or 0,
                'budget_count': summary_data['count']
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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