import os
import celery.result
from utils.core.test_core import TestRunner
import unittest
from celery import shared_task
from AutoTestDjango.settings.base import BASE_DIR
from test_task.models import TestTask


@shared_task()
def start_test(test_task_id: int, case_path: str):
    test_task = TestTask.objects.get(id=test_task_id)
    if not os.path.exists(BASE_DIR):
        raise ValueError('Path does not exist: {}'.format(BASE_DIR))
    # 1、加载测试用例到套件中
    suite = unittest.defaultTestLoader.discover(os.path.join(BASE_DIR, case_path))
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
        host=test_task.host
    )
    # 3、运行测试用例
    try:
        test_task.status = 2
        test_task.save()
        runner.run()
        return runner
    except Exception as e:
        test_task.status = 4
        test_task.save()
        raise e


