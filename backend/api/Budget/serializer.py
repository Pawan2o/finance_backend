from rest_framework import serializers
from api.Budget.model import Budget
from api.Category.serializer import CategorySerializer
from datetime import datetime
from dateutil.relativedelta import relativedelta


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    quarterly_start_date = serializers.DateField(write_only=True, required=False)
    
    class Meta:
        model = Budget
        fields = [
            'id', 
            'category',
            'category_name', 
            'category_details',
            'budget_type',
            'week',
            'month', 
            'year',
            'quarterly',
            'quarterly_start_date',
            'amount', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'quarterly']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # Auto-set budget_type based on provided fields
        if validated_data.get('week'):
            validated_data['budget_type'] = 'weekly'
        elif validated_data.get('month'):
            validated_data['budget_type'] = 'monthly'
        elif validated_data.get('quarterly_start_date') or validated_data.get('quarterly'):
            validated_data['budget_type'] = 'quarterly'
        elif validated_data.get('year'):
            validated_data['budget_type'] = 'yearly'
        
        # Handle quarterly budget with start date
        quarterly_start_date = validated_data.pop('quarterly_start_date', None)
        if quarterly_start_date and not validated_data.get('month') and not validated_data.get('week'):
            end_date = quarterly_start_date + relativedelta(months=3)
            validated_data['quarterly'] = f"{quarterly_start_date} to {end_date}"
        
        return super().create(validated_data)