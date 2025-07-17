# tasks/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer



class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create a new task"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'scheduled_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user).select_related('user')
        
        # Manual filtering
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        category = self.request.query_params.get('category')
        scheduled_date = self.request.query_params.get('scheduled_date')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category=category)
        if scheduled_date:
            queryset = queryset.filter(scheduled_date=scheduled_date)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # Check console for errors
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)



class TaskUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskSerializer


class UserTaskListView(generics.ListAPIView):
    """
    List all tasks for the logged-in user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # only authenticated users
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')    