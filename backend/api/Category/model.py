import uuid
from django.db import models
from api.Type.model import Type


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name="categories",
        db_index=True
    )

    name = models.CharField(max_length=255, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("type", "name")

    def __str__(self):
        return self.name