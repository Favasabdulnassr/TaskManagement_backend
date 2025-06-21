from django.urls import path
from .views import (
    TaskListCreateView,
    TaskUpdateView,
    UserTaskListView
)

urlpatterns = [
    # CRUD operations
    path('api/tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('api/tasks/Update/<uuid:pk>/', TaskUpdateView.as_view(), name='task-detail'),
    path('api/my-tasks/', UserTaskListView.as_view(), name='user-task-list'),

]