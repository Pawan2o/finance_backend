import uuid
from django.db import models
from dateutil.relativedelta import relativedelta

from api.User.model import CustomUser
from api.Type.model import Type
from api.Category.model import Category
from api.PaymentMethod.model import PaymentMethod


class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("quarterly", "Quarterly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recurring_transactions",
        db_index=True
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name="recurring_transactions",
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="recurring_transactions",
        db_index=True
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="recurring_transactions",
        db_index=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        db_index=True
    )
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True)
    next_run_date = models.DateField(db_index=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active', 'deleted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.frequency}"

    def calculate_next_run_date(self):
        """Calculate next run date based on frequency"""
        if self.frequency == "daily":
            return self.next_run_date + relativedelta(days=1)
        elif self.frequency == "weekly":
            return self.next_run_date + relativedelta(weeks=1)
        elif self.frequency == "monthly":
            return self.next_run_date + relativedelta(months=1)
        elif self.frequency == "quarterly":
            return self.next_run_date + relativedelta(months=3)
        elif self.frequency == "yearly":
            return self.next_run_date + relativedelta(years=1)
        return self.next_run_date