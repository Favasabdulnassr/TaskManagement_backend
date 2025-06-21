# tasks/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Task
from users.models import User


class TaskSerializer(serializers.ModelSerializer):
    user_firstName = serializers.CharField(source='user.first_name', read_only=True)
    is_scheduled_today = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'user_firstName', 'title', 'description', 
            'priority', 'status', 'category', 'scheduled_date', 
            'created_at', 'updated_at','completed_at','is_scheduled_today', 
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

    
    def validate_due_date(self, value):
        """Validate that due_date is not in the past"""
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    
    def validate_scheduled_date(self, value):
        """Validate that scheduled_date is not in the past"""
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Scheduled date cannot be in the past.")
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    class Meta:
        model = Task
        fields = [
            'user','title', 'description', 'priority', 'status', 'category',
            'scheduled_date'
        ]
    
    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    
    def validate_scheduled_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Scheduled date cannot be in the past.")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks"""
    
    class Meta:
        model = Task
        fields = '__all__'
    
    def update(self, instance, validated_data):
        # Auto-set completed_at when status changes to completed
        if validated_data.get('status') == 'completed' and instance.status != 'completed':
            validated_data['completed_at'] = timezone.now()
        
        # Clear completed_at when status changes from completed
        if instance.status == 'completed' and validated_data.get('status') != 'completed':
            validated_data['completed_at'] = None
        
        return super().update(instance, validated_data)
    

