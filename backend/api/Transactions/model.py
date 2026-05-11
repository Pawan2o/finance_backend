import uuid
from django.db import models
from api.User.model import CustomUser

from api.Type.model import Type
from api.Category.model import Category
from api.PaymentMethod.model import PaymentMethod


class Transaction(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_transaction_FK", db_index=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="type_transaction_FK", db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_transaction_FK", db_index=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="payment_method_transaction_FK", db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    transaction_date = models.DateField(db_index=True)
    description = models.TextField(blank=True, null=True)
    fingerprint = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"