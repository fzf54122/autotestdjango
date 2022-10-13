from django.http import JsonResponse, Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

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

    request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                  required=['host', 'project', 'version'], properties=
                                  {'host': openapi.Schema(type=openapi.TYPE_STRING, description='被测IP'),
                                   'project': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                                   'version': openapi.Schema(type=openapi.TYPE_STRING, description='版本号'),
                                   }
                                  )

    @swagger_auto_schema(method='post', request_body=request_body, )
    @action(methods=['post'], detail=False, )
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        serializer = TestTaskSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            # 创建任务
            result = self.run_method(start_test, test_task_id=instance.id)
            instance.uuid = result.id
            instance.status = 2
            instance.save()
            response = TestTaskResponseSerializer(instance)
            return JsonResponse(response.data, status=201)
        else:
            return Response(serializer.errors, status=401)

    query_param = openapi.Parameter(name='id', in_=openapi.IN_QUERY, description="查询id",
                                    type=openapi.TYPE_STRING)

    @swagger_auto_schema(method='get', manual_parameters=[query_param])
    @action(methods=['get'], detail=False)
    def get(self, request, *args, **kwargs):
        _id = self.request.query_params.get('id')
        task = self.get_object(_id)
        if task is Http404:
            return Response({}, status=200)
        else:
            serializer = TestTaskResponseSerializer(task)
            return Response(serializer.data, status=200)


class ReportView(APIView, CeleryTaskMixin):

    def get_object(self, pk):
        try:
            return TestTask.objects.get(pk=pk)
        except TestTask.DoesNotExist:
            return Http404

    query_param = openapi.Parameter(name='id', in_=openapi.IN_QUERY, description="查询id",
                                    type=openapi.TYPE_STRING)

    @swagger_auto_schema(method='get', manual_parameters=[query_param])
    @action(methods=['get'], detail=False)
    def get(self, request, *args, **kwargs):
        _id = self.request.query_params.get('id')
        task = self.get_object(_id)
        report_file = f'{task.uuid}.html'
        if task is Http404:
            return Response({}, status=200)
        else:
            serializer = TestTaskResponseSerializer(task)
            print('serializer', serializer.data)
            return Response(serializer.data, status=200)
