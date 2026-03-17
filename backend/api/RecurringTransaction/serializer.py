from rest_framework import serializers
from dateutil.relativedelta import relativedelta
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
    end_date = serializers.DateField(required=False)

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
        frequency = data.get("frequency")
        amount = data.get("amount")

        # Auto-calculate end_date based on frequency if not provided
        if start_date and frequency and not end_date:
            if frequency == "quarterly":
                data["end_date"] = start_date + relativedelta(months=3)
            elif frequency == "daily":
                data["end_date"] = start_date + relativedelta(days=1)
            elif frequency == "weekly":
                data["end_date"] = start_date + relativedelta(weeks=1)
            elif frequency == "monthly":
                data["end_date"] = start_date + relativedelta(months=1)
            elif frequency == "yearly":
                data["end_date"] = start_date + relativedelta(years=1)

        if data.get("end_date") and start_date and data["end_date"] < start_date:
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