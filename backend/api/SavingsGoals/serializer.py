from rest_framework import serializers
from .model import SavingsGoals
from api.Category.serializer import CategorySerializer

class SavingsGoalsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    saved_amount = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    target_category_name = serializers.CharField(source='target_category.name', read_only=True)
    target_category_details = CategorySerializer(source='target_category', read_only=True)
    
    class Meta:
        model = SavingsGoals
        fields = [
            'id', 
            'user_name', 
            'goal_name', 
            'target_amount', 
            'saved_amount',
            'progress_percentage',
            'remaining_amount',
            'target_category',
            'target_category_name',
            'target_category_details',
            'deadline', 
            'status', 
            'description',
            'start_date',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'user_name', 
            'saved_amount', 'progress_percentage', 'remaining_amount',
            'target_category_name', 'target_category_details', 'start_date'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavingsGoalsDetailSerializer(SavingsGoalsSerializer):
    """Detailed serializer with related transactions"""
    related_transactions_count = serializers.SerializerMethodField()
    
    class Meta(SavingsGoalsSerializer.Meta):
        fields = SavingsGoalsSerializer.Meta.fields + ['related_transactions_count']
    
    def get_related_transactions_count(self, obj):
        return obj.get_related_transactions().count()