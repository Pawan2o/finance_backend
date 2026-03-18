from rest_framework import serializers
from api.Budget.model import Budget
from api.Type.serializer import TypeSerializer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BudgetSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    type_details = TypeSerializer(source='type', read_only=True)
    quarterly_start_date = serializers.DateField(required=False)
    quarterly_end_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 
            'type',
            'type_name', 
            'type_details',
            'budget_type',
            'week',
            'month', 
            'year',
            'quarterly_start_date',
            'quarterly_end_date',
            'amount', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'quarterly_end_date']

    def validate(self, data):
        budget_type = data.get('budget_type')
        
        if budget_type == 'monthly':
            if not (data.get('month') and data.get('year')):
                raise serializers.ValidationError("Month and year are required for monthly budget")
        
        elif budget_type == 'weekly':
            if not (data.get('week') and data.get('year')):
                raise serializers.ValidationError("Week and year are required for weekly budget")
        
        elif budget_type == 'quarterly':
            if not data.get('quarterly_start_date'):
                raise serializers.ValidationError("Quarterly start date is required for quarterly budget")
        
        elif budget_type == 'yearly':
            if not data.get('year'):
                raise serializers.ValidationError("Year is required for yearly budget")
        
        return data

    def create(self, validated_data):
        # Handle quarterly budget with start date
        quarterly_start_date = validated_data.get('quarterly_start_date')
        if quarterly_start_date and validated_data.get('budget_type') == 'quarterly':
            # Calculate end date: 3 months - 1 day
            end_date = quarterly_start_date + relativedelta(months=3) - timedelta(days=1)
            validated_data['quarterly_end_date'] = end_date
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle quarterly budget updates
        quarterly_start_date = validated_data.get('quarterly_start_date')
        if quarterly_start_date and validated_data.get('budget_type') == 'quarterly':
            end_date = quarterly_start_date + relativedelta(months=3) - timedelta(days=1)
            validated_data['quarterly_end_date'] = end_date
        
        return super().update(instance, validated_data)