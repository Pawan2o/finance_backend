from rest_framework import serializers
from api.Budget.model import Budget
from api.Category.serializer import CategorySerializer


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 
            'category',
            'category_name', 
            'category_details',
            'week',
            'month', 
            'year', 
            'amount', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)