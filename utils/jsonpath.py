from typing import Dict
from jsonpath_ng import parse


class JsonPath:

    def __init__(self, data):
        self._data: Dict = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, dict):
            self._data = value
        else:
            raise TypeError("value must be a dict")

    def search(self, expression):
        """查找内容"""
        jsonpath_expr = parse(expression)
        matches = jsonpath_expr.find(self.data)
        # find返回的为match对象列表，找到的值存储在value属性中
        return [match.value for match in matches]


