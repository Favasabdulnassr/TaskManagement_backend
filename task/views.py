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


class TaskViewSet(ModelViewSet):
    """
    ViewSet for managing tasks with full CRUD operations
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'scheduled_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return tasks for the authenticated user only with filtering"""
        queryset = Task.objects.filter(user=self.request.user).select_related('user')
        
        # Manual filtering since we're not using django-filter
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
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a task"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a task as completed"""
        task = self.get_object()
        task.mark_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks scheduled for today"""
        today_tasks = self.get_queryset().filter(scheduled_date=timezone.now().date())
        serializer = self.get_serializer(today_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)"""
        next_week = timezone.now() + timezone.timedelta(days=7)
        upcoming_tasks = self.get_queryset().filter(
            due_date__range=[timezone.now(), next_week],
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(upcoming_tasks, many=True)
        return Response(serializer.data)


# Alternative individual class-based views if you prefer not to use ViewSet

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



class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a task"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskSerializer


class TasksByStatusView(generics.ListAPIView):
    """Get tasks filtered by status"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        status = self.kwargs.get('status')
        return Task.objects.filter(
            user=self.request.user, 
            status=status
        ).select_related('user')


class TasksByPriorityView(generics.ListAPIView):
    """Get tasks filtered by priority"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        priority = self.kwargs.get('priority')
        return Task.objects.filter(
            user=self.request.user, 
            priority=priority
        ).select_related('user')


class TodayTasksView(generics.ListAPIView):
    """Get tasks scheduled for today"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user,
            scheduled_date=timezone.now().date()
        ).select_related('user')


class OverdueTasksView(generics.ListAPIView):
    """Get overdue tasks"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).select_related('user')