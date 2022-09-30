import os
from django.http import JsonResponse, Http404
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from test_task.models import TestTask
from test_task.serializers import TestTaskSerializer, TestTaskResponseSerializer
from test_task.tasks import start_test
from utils.core.view_mixin import CeleryTaskMixin


# Create your views here.
class TestTaskView(APIView, CeleryTaskMixin):

    def get_object(self, pk):
        try:
            return TestTask.objects.get(pk=pk)
        except TestTask.DoesNotExist:
            return Http404

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        serializer = TestTaskSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            case_path = os.path.join('test_cases', instance.project, instance.version)
            # 创建任务
            result = self.run_method(start_test, test_task_id=instance.id, case_path=case_path)

            instance.uuid = result.id
            instance.status = 2
            instance.save()
            response = TestTaskResponseSerializer(instance)
            return JsonResponse(response.data, status=201)
        else:
            return Response(serializer.errors, status=401)

    def get(self, request, *args, **kwargs):

        _id = self.request.query_params.get('id')
        task = self.get_object(_id)
        if task is Http404:
            return Response({}, status=200)
        else:
            serializer = TestTaskResponseSerializer(task)
            return Response(serializer.data, status=200)
