from rest_framework import serializers
from .model import Transaction



class TransactionSerializer(serializers.ModelSerializer):

    type_name = serializers.CharField(source="type.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    payment_method_name = serializers.CharField(source="payment_method.payment_method",read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "deleted_at"
        ]