from rest_framework import serializers
from api.Category.model import Category


class CategorySerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        # Check only active records (not soft-deleted)
        queryset = Category.objects.filter(name=value, deleted_at__isnull=True)
        
        # Exclude current instance during update
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        
        return value

    class Meta:
        model = Category
        fields = [
            "id",
            "type",
            "name",
            "material_icon",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]