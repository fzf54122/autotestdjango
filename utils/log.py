from functools import wraps
import logging
from rich.logging import RichHandler


default_level = logging.INFO


def get_logger(name, level=default_level):
    return _get_rich_logger(name, level)


def _get_standard_logger(name, level=default_level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    FORMAT = "[%(asctime)s][%(levelname)s][%(filename)s][line %(lineno)s][%(funcName)5s()]: %(message)s"
    formatter = logging.Formatter(FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def _get_rich_logger(name, level=default_level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    FORMAT = "[%(filename)s][line %(lineno)s][%(funcName)5s()]: %(message)s"
    formatter = logging.Formatter(FORMAT)
    console_handler = RichHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def logged(name=None, level=None):
    """
    日志装饰器，会捕获被装饰的方法
    name: logger名称，未提供则默认是被修饰func的名称
    level: 日志等级，支持logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
    """

    def decorate(func):
        log_name = name if name is not None else func.__name__
        log_level = level if level is not None else default_level
        logger = get_logger(log_name, log_level)

        @wraps(func)
        def wrap_func(*args, **kwargs):
            tuple_args = args
            dict_kwargs = kwargs
            try:
                result = func(*args, **kwargs)
                logger.debug(f'{func.__name__}(*args: tuple = *{tuple_args}, **kwargs: dict = **{dict_kwargs})')
                return result
            except Exception as e:
                logger.exception(f'{func.__name__}(*args: tuple = *{tuple_args}, **kwargs: dict = **{dict_kwargs})',
                                 exc_info=True)
                # 记录错误后将错误抛出
                raise e
        return wrap_func
    return decorate
