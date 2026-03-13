from rest_framework import serializers
from api.RecurringTransaction.model import RecurringTransaction


class RecurringTransactionSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="type.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    payment_method_name = serializers.CharField(
        source="payment_method.payment_method",
        read_only=True
    )
    user_name = serializers.CharField(source="user.username", read_only=True)
    next_run_date = serializers.DateField(required=False)

    class Meta:
        model = RecurringTransaction
        fields = [
            "id",
            "user",
            "user_name",
            "type",
            "type_name",
            "category",
            "category_name",
            "payment_method",
            "payment_method_name",
            "amount",
            "frequency",
            "start_date",
            "end_date",
            "next_run_date",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        amount = data.get("amount")

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be earlier than start date."}
            )

        if amount and amount <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be greater than zero."}
            )

        # Auto-set next_run_date to start_date if not provided
        if not data.get("next_run_date") and start_date:
            data["next_run_date"] = start_date

        return data