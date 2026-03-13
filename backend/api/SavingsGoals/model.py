import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, Q
from api.User.model import CustomUser
from api.Category.model import Category

class SavingsGoals(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="savings_goals",
        db_index=True
    )
    
    goal_name = models.CharField(max_length=100, db_index=True)
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        db_index=True
    )
    
    # Optional: Filter transactions by category
    target_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Filter transactions by category for this goal"
    )
    
    deadline = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    description = models.TextField(blank=True, null=True)
    
    # Track when goal was started
    start_date = models.DateField(auto_now_add=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at', 'deadline']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['deadline', 'status']),
            models.Index(fields=['start_date', 'user']),
        ]
        
    def __str__(self):
        return f"{self.goal_name} - {self.user.username}"
    
    @property
    def saved_amount(self):
        """Calculate saved amount from user's all transactions (income - expense)"""
        from api.Transactions.model import Transaction
        
        # Get ALL user transactions (no date filter for now)
        transactions = Transaction.objects.filter(
            user=self.user,
            deleted_at__isnull=True
        )
        
        # Filter by category if specified
        if self.target_category:
            transactions = transactions.filter(category=self.target_category)
        
        # Calculate income and expense
        income_total = 0
        expense_total = 0
        
        for transaction in transactions:
            if transaction.type.name.lower() == 'income':
                income_total += transaction.amount
            elif transaction.type.name.lower() == 'expense':
                expense_total += transaction.amount
        
        # Calculate savings (income - expense)
        savings = income_total - expense_total
        
        # Return minimum of savings or target amount
        return max(0, min(float(savings), float(self.target_amount)))
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return min((float(self.saved_amount) / float(self.target_amount)) * 100, 100)
        return 0
    
    @property
    def remaining_amount(self):
        return max(float(self.target_amount) - float(self.saved_amount), 0)
    
    def get_related_transactions(self):
        """Get transactions that contribute to this goal"""
        from api.Transactions.model import Transaction
        
        transactions = Transaction.objects.filter(
            user=self.user,
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.deadline,
            deleted_at__isnull=True
        )
        
        if self.target_category:
            transactions = transactions.filter(category=self.target_category)
            
        return transactions.order_by('-transaction_date')