from django.conf import settings


class CeleryTaskMixin:
    task = None
    test = settings.TEST

    def run(self, *args, **kwargs):
        """delay方式运行"""
        if self.test:
            return self.task(*args, **kwargs)
        else:
            return self.task.delay(*args, **kwargs)

    def run_async(self, task, *args, **kwargs):
        """异步任务执行，eta参数指定任务需要执行的时间；expires参数设置失效时间，超过该时间后，任务不会再执行"""
        eta = kwargs.pop('eta')
        expires = kwargs.pop('expires') if 'expires' in kwargs else None
        if self.test:
            return task(*args, **kwargs)
        else:
            return task.apply_async(args, kwargs, eta=eta, expires=expires)

    def run_method(self, task, *args, **kwargs):
        """
        执行指定的任务，一般使用run方法即可，如果视图里有很多任务需要执行，就调用这个方法
        手动传入需要执行的任务
        :param task: 指定的任务
        :param args: 任务传递参数
        :param kwargs:
        :return:
        """
        if self.test:
            return task(*args, **kwargs)
        else:
            return task.delay(*args, **kwargs)

