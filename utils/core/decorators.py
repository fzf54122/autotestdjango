from functools import wraps
import logging
import os
import unittest


def singleton(cls):
    """单例装饰器"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


class DependencyError(Exception):

    def __int__(self, _type=0):
        self._type = _type

    def __str__(self):
        if self._type == 0:
            return f'Dependency name of test is required!'
        if self._type == 1:
            return f'Dependency name of test can not the case self!'


def depends_on(case=''):
    """用例依赖装饰器"""
    if not case:
        raise DependencyError
    _mark = []

    def wrap_func(func):
        @wraps(func)
        def inner_func(self):
            # 检查循环依赖
            if case == func.__name__:
                raise DependencyError(1)
            _r = self._outcome.result
            _f, _e, _s = _r.failures, _r.errors, _r.skipped

            # 如果还无失败、错误、跳过记录
            if not (_f or _e or _s):
                return func(self)
            # 三种状态的用例放入集合中
            if _f:
                _mark.extend([fail[0] for fail in _f])
            if _e:
                _mark.extend([error[0] for error in _e])
            if _s:
                _mark.extend([skip[0] for skip in _s])

            unittest.skipIf(
                case in str(_mark),
                f'The pre-depend case :{case} has failed! Skip the specified case!'
            )(func)(self)
        return inner_func
    return wrap_func

