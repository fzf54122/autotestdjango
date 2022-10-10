import logging
import os
import celery.result
from utils.core.test_core import TestRunner
import unittest
from celery import shared_task
from AutoTestDjango.settings.base import BASE_DIR
from test_task.models import TestTask, SummaryReport
from utils.core.test_core.loader import BoleanLoader
from utils.core.session import *
import importlib


@shared_task()
def start_test(test_task_id: int):
    instance = TestTask.objects.get(id=test_task_id)
    if not os.path.exists(BASE_DIR):
        raise ValueError('Path does not exist: {}'.format(BASE_DIR))

    # 准备全局依赖的测试数据， prepare需要在project目录下的prepare文件中
    has_preparation = True
    prepare_module = None
    try:
        prepare_module = importlib.import_module('test_cases.{}.prepare'.format(instance.project))
    except ImportError:
        has_preparation = False
    if has_preparation:
        prepare_cls = getattr(prepare_module, 'Preparation', None)
        if not prepare_cls:
            instance.status = 4
            instance.save()
            raise RuntimeError('No Preparation class found in prepare module')
        prepare_cls.session.host = instance.host
        for item in prepare_cls.__dict__:
            if item.startswith('prepare'):
                prepare_method = getattr(prepare_cls, item)
                prepare_method()

    # 加载并执行用例
    # 1、加载测试用例到套件中
    case_path = os.path.join('test_cases', instance.project)
    suite = BoleanLoader().discover(start_dir=os.path.join(BASE_DIR, case_path),
                                    version=instance.version, tags=instance.tags)
    report_path = os.path.join(BASE_DIR, 'media/reports')
    task_name = celery.current_task.request.id
    # 2、创建一个用例运行程序
    runner = TestRunner(
        suite,
        tester='自动化',
        filename=f'{task_name}.html',
        report_dir=report_path,
        title='自动化测试',
        desc='自动化测试',
        templates=2,
        host=instance.host
    )
    # 3、运行测试用例
    try:
        runner.run()
        instance.status = 3
        report = SummaryReport(**runner.test_result)
        instance.report = report.json()
        # test_task.result = runner.result.__dict__
    except Exception as e:
        logging.error(e.__repr__())
        instance.status = 4
    finally:
        instance.save()
