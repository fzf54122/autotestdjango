from django.urls import path, include
from rest_framework.routers import SimpleRouter

from test_task import views

router = SimpleRouter()

urlpatterns = [
    path('task/', views.TestTaskView.as_view(), name='test-task'),
]
