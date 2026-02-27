from rest_framework import serializers
from api.Type.model import Type
from api.Category.model import Category


class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TypeSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Type
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "categories"
        ]

    def get_categories(self, obj):
        categories = obj.categories.filter(deleted_at__isnull=True)
        return CategoryNestedSerializer(categories, many=True).data