from django.urls import path
from .views import (
    TaskListCreateView,
    TaskUpdateView,
    TasksByStatusView,
    TasksByPriorityView,
    TodayTasksView,
    OverdueTasksView,
)

urlpatterns = [
    # CRUD operations
    path('api/tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('api/tasks/Update/<uuid:pk>/', TaskUpdateView.as_view(), name='task-detail'),

    # Filtered tasks
    path('api/tasks/status/<str:status>/', TasksByStatusView.as_view(), name='tasks-by-status'),
    path('api/tasks/priority/<str:priority>/', TasksByPriorityView.as_view(), name='tasks-by-priority'),

    # Special views
    path('api/tasks/today/', TodayTasksView.as_view(), name='tasks-today'),
    path('api/tasks/overdue/', OverdueTasksView.as_view(), name='tasks-overdue'),
]