import uuid
from django.db import models

class PaymentMethod(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_method = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.payment_method