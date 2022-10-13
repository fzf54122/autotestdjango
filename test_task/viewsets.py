from rest_framework.viewsets import ModelViewSet

from test_task.models import TestTask
from test_task.serializers import TestTaskSerializer


class testViewSet(ModelViewSet):
    serializer_class = TestTaskSerializer
    queryset = TestTask.objects.all()
