import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from api.Category.model import Category
from api.User.model import CustomUser

class Budget(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="budgets",
        db_index=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
        db_index=True
    )

    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        db_index=True
    )
    year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        db_index=True
    )
    
    week = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(53)],
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
        unique_together = ["user", "category", "month", "year"]
        ordering = ["-year", "-month", "category__name"]
        indexes = [
            models.Index(fields=["user", "year", "month"]),
            models.Index(fields=["category", "year", "month"]),
        ]
    def __str__(self):
        if self.week is not None:
            return f"{self.user.username} - {self.category.name} (Week {self.week}/{self.year})"
        
        if self.month is not None:
            return f"{self.user.username} - {self.category.name} ({self.month:02d}/{self.year})"
        
        return f"{self.user.username} - {self.category.name} ({self.year})"