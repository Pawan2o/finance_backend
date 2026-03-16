import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from api.Type.model import Type
from api.User.model import CustomUser

class Budget(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="budgets",
        db_index=True
    )

    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name="budgets",
        db_index=True
    )

    BUDGET_TYPE_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    budget_type = models.CharField(
        max_length=20,
        choices=BUDGET_TYPE_CHOICES,
        db_index=True,
        default='monthly'
    )

    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True,
        db_index=True
    )
    year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        null=True,
        blank=True,
        db_index=True
    )
    
    week = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(53)],
        null=True,
        blank=True,
        db_index=True
    )
    
    quarterly_start_date = models.DateField(
        null=True,
        blank=True,
        db_index=True
    )
    
    quarterly_end_date = models.DateField(
        null=True,
        blank=True,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'type', 'budget_type', 'month', 'year'],
                condition=models.Q(budget_type='monthly'),
                name='unique_monthly_budget'
            ),
            models.UniqueConstraint(
                fields=['user', 'type', 'budget_type', 'week', 'year'],
                condition=models.Q(budget_type='weekly'),
                name='unique_weekly_budget'
            ),
            models.UniqueConstraint(
                fields=['user', 'type', 'budget_type', 'quarterly_start_date'],
                condition=models.Q(budget_type='quarterly'),
                name='unique_quarterly_budget'
            ),
            models.UniqueConstraint(
                fields=['user', 'type', 'budget_type', 'year'],
                condition=models.Q(budget_type='yearly'),
                name='unique_yearly_budget'
            ),
        ]
        ordering = ["-created_at", "type__name"]
        indexes = [
            models.Index(fields=["user", "year", "month"]),
            models.Index(fields=["type", "year", "month"]),
            models.Index(fields=["user", "quarterly_start_date"]),
            models.Index(fields=["quarterly_start_date", "quarterly_end_date"]),
            models.Index(fields=["budget_type"]),
        ]
    def __str__(self):
        if self.week is not None:
            return f"{self.user.username} - {self.type.name} (Week {self.week}/{self.year})"
        
        if self.quarterly_start_date is not None:
            return f"{self.user.username} - {self.type.name} ({self.quarterly_start_date} to {self.quarterly_end_date})"
        
        if self.month is not None:
            return f"{self.user.username} - {self.type.name} ({self.month:02d}/{self.year})"
        
        return f"{self.user.username} - {self.type.name} ({self.year})"