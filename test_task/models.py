from django.db import models
# import time
# from abc import ABC, abstractmethod
# from typing import List
#
# import uuid
# from django.contrib.postgres.fields import ArrayField
# from django.db import models
# from django.db.models import IntegerField, CharField, BooleanField, JSONField, ForeignKey
# from pydantic import BaseModel, validator
# Create your models here.

# Create your models here.

# operator_map = (
#     ("==", "__eq__"),
#     ("!=", "!__nq__"),
#     (">", "__gt__"),
#     (">=", "__ge__"),
#     ("<", "__lt__"),
#     ("<=", "__le__"),
#     ("in", "__contains__"),
#     ("not in", "!__contains__"),
#     ('is none', "")
# )
#
#
# class IController(ABC):
#
#     @abstractmethod
#     def run(self):
#         ...
#
#
# class ScriptController(IController):
#
#     def run(self):
#         ...
#
#
# class HttpRequestController(ScriptController):
#     def __init__(self, request):
#         pass
#
#     def run(self):
#         self.prepare()
#         self.request()
#         self.post()
#
#     def request(self):
#         pass
#
#     def prepare(self):
#         pass
#
#     def post(self):
#         pass
#
#
# class CodeController(ScriptController):
#     def run(self):
#         ...
#
#
# class LogicController(IController):
#     def run(self):
#         ...
#
#
# class IfController(LogicController):
#
#     def __init__(self, a, operator, b=None):
#         self.a = a
#         self.operator = operator
#         self.b = b
#         self.sub_controllers: List[IController] = []
#
#     def run(self):
#         # 检查当前状态
#         if self._check_condition():
#             # 执行子控制器
#             for sub_controller in self.sub_controllers:
#                 sub_controller.run()
#         else:
#             return
#
#     def _check_condition(self):
#         if self.operator == '==':
#             return self.a == self.b
#         elif self.operator == '!=':
#             return self.a != self.b
#         elif self.operator == '>':
#             return self.a > self.b
#         elif self.operator == '>=':
#             return self.a >= self.b
#         elif self.operator == '<':
#             return self.a < self.b
#         elif self.operator == '<=':
#             return self.a <=  self.b
#         elif self.operator == 'in':
#             return self.a in self.b
#         elif self.operator == 'not in':
#             return self.a not in self.b
#         elif self.operator == 'is None':
#             return self.a is None
#         elif self.operator == 'is not None':
#             return self.a is not None
#         else:
#             raise ValueError('Invalid operator')
#
#
# class WhileController(LogicController):
#
#     def __init__(self, condition: IfController, interval: int = None, timeout: int = None):
#         self.condition = condition
#         self.interval = float(interval / 1000) if interval is not None else None
#         self.timeout = float(timeout / 1000) if timeout is not None else None
#         self.sub_controllers: List[IController] = []
#
#     def run(self):
#         start_time = time.time()
#         while self.condition.run():
#             for sub_controller in self.sub_controllers:
#                 sub_controller.run()
#             if self.interval is not None:
#                 time.time()
#             current_time = time.time()
#             if (current_time - start_time) > self.timeout:
#                 break
#         return
#
#
# class ForController(LogicController):
#
#     def __init__(self, count, interval=None):
#         self.count = count
#         self.interval = float(interval / 1000) if interval is not None else None
#         self.sub_controllers: List[IController] = []
#
#     def run(self):
#         for i in range(self.count):
#             for sub_controller in self.sub_controllers:
#                 sub_controller.run()
#             if self.interval is not None:
#                 time.sleep(self.interval)


STATE_CHOICES = [
    (1, ' 未开始'),
    (2, '运行中'),
    (3, '成功'),
    (4, '失败')
]


class TestTask(models.Model):
    host = models.CharField(max_length=50, verbose_name='被测主机')
    project = models.CharField(max_length=50, verbose_name='被测产品')
    version = models.CharField(max_length=50, verbose_name='产品版本')
    uuid = models.UUIDField(verbose_name='用于任务标识的uuid', null=True)
    status = models.IntegerField(choices=STATE_CHOICES, verbose_name='任务状态', default=1)
    result = models.JSONField(max_length=10, verbose_name='任务结果', null=True)

    class Meta:
        verbose_name = '测试任务'
        ordering = ('-id',)
