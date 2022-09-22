from rest_framework import serializers
from test_task.models import TestTask


class TestTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestTask
        fields = ['host', 'project', 'version']


class TestTaskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestTask
        fields = ['id', 'status', 'host', 'project', 'version', 'result']
