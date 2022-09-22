import re
from abc import ABC, abstractmethod
from typing import List, Union, Dict
from pydantic import BaseModel, validator
from requests import Response
from utils.log import get_logger
from utils.core.decorators import singleton
from utils.jsonpath import JsonPath
import requests


logger = get_logger(__name__)


operator_map = (
    ('==', 'assert_equal'),
    ("!=", 'assert_not_equal'),
    (">", 'assert_greater_than'),
    ("<", 'assert_less_than'),
    (">=", 'assert_greater_than_or_equal'),
    ("<=", 'assert_less_than_or_equal'),
    ("re.match", "assert_match"),
    ("is", 'assert_is_instance')
)


@singleton
class AssertionOperator:
    """断言操作"""
    failureException = AssertionError

    def assert_equal(self, actual, expected, msg=None):
        """断言相等"""
        logger.debug(f"Got param: actual={actual}:{type(actual)}, expected={expected}:{type(expected)}, msg={msg}")
        if not actual == expected:
            raise self.failureException(msg or f"{actual} == {expected}")

    def assert_not_equal(self, actual, expected, msg=None):
        """断言不等"""
        if actual == expected:
            raise self.failureException(msg or f"{actual} != {expected}")

    def assert_true(self, expr, msg=None):
        """断言表达式为真"""
        if not expr:
            raise self.failureException(msg)

    def assert_false(self, expr, msg=None):
        """断言表达式为假"""
        if expr:
            raise self.failureException(msg)

    def assert_error(self, exc_class, callable_obj, *args, **kwargs):
        """断言可调用的对象是否返回指定类型的错误"""
        try:
            callable_obj(*args, **kwargs)
        except exc_class:
            return
        else:
            if hasattr(exc_class, '__name__'):
                exc_name = exc_class.__name__
            else:
                exc_name = str(exc_class)
            raise self.failureException(f"{exc_name} not raised")

    def assert_in(self, member, container, msg=None):
        """断言元素在对象内，一般为sequence"""
        if member not in container:
            raise self.failureException(msg or f"{member} in {container}")

    def assert_not_in(self, member, container, msg=None):
        """断言元素不在对象内"""
        if member in container:
            raise self.failureException(msg or f"{member} not in {container}")

    def assert_is_instance(self, actual, expected, msg=None):
        """断言对象是指定类的实例或其子类的实例"""
        if actual is not expected:
            raise self.failureException(msg or f"{actual} is a {expected}")

    def assert_is_not_instance(self, obj, cls, msg=None):
        """断言对象不是指定类的实例"""
        if isinstance(obj, cls):
            raise self.failureException(msg or f"{obj} is not a {cls}")

    def assert_greater_than(self, actual, expected, msg=None):
        """断言a大于等于b"""
        if not actual > expected:
            raise self.failureException(msg or f"{actual} > {expected}")

    def assert_less_than(self, actual, expected, msg=None):
        """断言a小于b"""
        if actual > expected:
            raise self.failureException(msg or f"{actual} < {expected}")

    def assert_greater_than_or_equal(self, actual, expected, msg=None):
        """断言a大于等于b"""
        if not actual >= expected:
            raise self.failureException(msg or f"{actual} >= {expected}")

    def assert_less_than_or_equal(self, actual, expected, msg=None):
        """断言a小于等于b"""
        if not actual <= expected:
            raise self.failureException(msg or f"{actual} <= {expected}")

    def assert_match(self, actual, expected, msg=None):
        """断言pattern可以匹配到content"""
        if not re.match(expected, actual):
            raise self.failureException(msg or f"{expected} match {actual}")


class AssertionActual(BaseModel):
    """响应提取信息"""
    type: str
    expression: str = None


class AssertionExpression(BaseModel):
    """断言表达式，包含actual、expected、operator"""
    actual: AssertionActual
    expected: object
    operator: str

    @validator('operator')
    def check_operator(cls, value):
        """检查操作信息正确性"""
        for op, fn in operator_map:
            if value == op:
                return value
        else:
            raise ValueError(f'value must be one of the first element in {operator_map}')


class ExtractStrategy(ABC):
    """抽象提取策略，需实现提取接口"""

    @abstractmethod
    def extract(self, content, rule):
        ...


class JsonPathExtractStrategy(ExtractStrategy):
    """JsonPath提取策略"""

    def extract(self, content: Union[Response, Dict], rule: str) -> List:
        """提取响应内容，返回列表对象，包含所有匹配到的结果"""
        json_repr = content
        if not isinstance(content, dict):
            json_repr = content.json()
        jp = JsonPath(json_repr)
        return jp.search(rule)


class ResponseStrategy(ExtractStrategy):
    """响应内容提取策略"""

    def extract(self, content, rule):
        key_seq = rule.split('.')


class ExtractStrategyFactory:
    """提取策略工厂"""
    strategy_map: dict = {}

    @classmethod
    def create_strategy(cls, actual: AssertionActual) -> ExtractStrategy:
        """创建提取策略"""
        if actual.type == 'jsonpath':
            if actual.type not in cls.strategy_map.keys():
                cls.strategy_map[actual.type] = JsonPathExtractStrategy()
        return cls.strategy_map[actual.type]


class AssertionHandler:
    """断言由三部分组成，待处理的载荷，断言配置（包含actual提取配置，操作符，期望内容）"""
    def __init__(self, response: Union[Response, Dict], assertion):
        self.response = response
        self.assertion = AssertionExpression(**assertion)

    def handle(self):
        """处理断言部分"""
        # 提取actual
        strategy = ExtractStrategyFactory.create_strategy(self.assertion.actual)
        actualities = strategy.extract(self.response, self.assertion.actual.expression)
        for actuality in actualities:
            # 映射operator
            for op, fn in operator_map:
                if op == self.assertion.operator:
                    ao = AssertionOperator()
                    func = getattr(ao, fn)
                    logger.debug(type(self.assertion.expected))
                    func(actuality, self.assertion.expected)


if __name__ == "__main__":
    # strategy = JsonPathStrategy()
    # assertion = {
    #     "actual": {
    #         "type": "jsonpath",
    #         "expression": "$.count"
    #     },
    #     "operator": "!=",
    #     "expected": 26
    # }
    # ae = AssertionExpression(**assertion)
    # content = {"count": 27, "next":"http://10.30.6.2/api/v1/scene/?ordering=&page=2&page_size=8&search=&status=",
    # "previous":None,"results":[{"id":67,"name":"【0905观安】PWN","memory":0,"status":2,"tags":["实验"],"update_time":"2022-09-02T10:27:10.527698+08:00","description":"","thumbnail":"/range/scene/2022-09-02T03:17:57.178702+00:00【0905观安】PWN"},{"id":66,"name":"用户演示","memory":4,"status":1,"tags":["竞赛"],"update_time":"2022-09-01T16:34:36.753442+08:00","description":"","thumbnail":"/range/scene/2022-09-02T02:46:40.285599+00:00用户演示"},{"id":62,"name":"【0905观安】场景题2","memory":4,"status":1,"tags":["竞赛"],"update_time":"2022-09-01T16:32:56.170892+08:00","description":"","thumbnail":"/range/scene/2022-09-02T05:58:22.651702+00:00【0905观安】场景题2"},{"id":65,"name":"11122","memory":4,"status":1,"tags":["实验"],"update_time":"2022-09-01T11:30:09.230478+08:00","description":"rr","thumbnail":"/range/scene/2022-09-01T10:17:57.282282+00:0011122"},{"id":61,"name":"容器测试","memory":0,"status":1,"tags":["测试"],"update_time":"2022-09-01T09:36:28.094709+08:00","description":"","thumbnail":"/range/scene/2022-09-01T09:48:21.841316+00:00容器测试"},{"id":60,"name":"9月5号比赛场景题目","memory":10,"status":6,"tags":["竞赛"],"update_time":"2022-09-01T09:36:01.057531+08:00","description":"勿删","thumbnail":"/range/scene/2022-09-02T03:26:39.466335+00:009月5号比赛场景题目"},{"id":57,"name":"测试容器虚拟机","memory":6,"status":1,"tags":["攻防"],"update_time":"2022-08-26T10:19:21.923364+08:00","description":"1","thumbnail":"/range/scene/2022-09-01T10:11:57.334886+00:00测试容器虚拟机"},{"id":56,"name":"临时使用，勿删","memory":4,"status":1,"tags":["测试"],"update_time":"2022-08-25T16:18:49.580221+08:00","description":"","thumbnail":"/range/scene/2022-09-01T06:20:54.813975+00:00临时使用，勿删"}]}
    # ah = AssertionHandler(response=content, assertion=assertion)
    # ah.handle()
    # expr = "$.results.[*]"
    # result = strategy.extract(content, expr)
    # print(result)
    resp = requests.request('GET', 'https://baidu.com/')
    print(resp.__dict__)
    ...
