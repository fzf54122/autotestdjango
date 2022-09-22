import json
from typing import List

from utils.file_reader import JsonReader
from utils.log import get_logger
from utils.exceptions import ParamException


logger = get_logger(__file__)


class SwaggerParser:

    def __init__(self, swagger_path: str = None, swagger_url: str = None):
        if not swagger_path and not swagger_url:
            raise ParamException(swagger_path, swagger_url)
        elif not swagger_url:
            # 提供了json文件
            self._json_path = swagger_path
        elif not swagger_path:
            # 提供了url
            self._json_url = swagger_url

    @property
    def data(self):
        return JsonReader(json_path=self._json_path).data

    def get_brief_info(self):
        ops = []
        for path in self.data['paths'].keys():
            methods = self.data['paths'][path].keys()  # methods are keys inside a single path-dict
            ops.append((f"{'|'.join(methods).upper()}", f"{path}"))
        return ops

    def get_request_info(self, path: str, method: str = None) -> dict:
        """
        获取request info 信息
        :param path: 需要处理的path
        :param method: 需要处理的method类型
        :return: 以dict返回，key为method， value为对应的request info
        """
        path_body = self.data['paths'][path]
        res: dict = {}
        if not method:
            for m in path_body.keys():
                res[m] = path_body[m]
        else:
            res[method] = path_body[method.lower()]
        return res

    def get_param_schema(self, path: str = None, method: str = None, content_type: str = 'application/json'):
        """
        获取 指定接口 && 指定方法 && 指定content_type的请求参数的schema
        :param path: 指定获取的接口， 默认为None
        :param method: 指定获取的请求方法， 默认为None
        :param content_type: 指定获取的content_type， 默认为application/json
        :return: 以dict的形式返回schema
        """
        if not path or not method or method.lower() not in self.get_supported_method(path):
            raise ParamException(method, content_type)
        else:
            try:
                path_body = self.data['paths'][path]
                return path_body[method]['requestBody']['content'][content_type].get('schema', None)
            except Exception as e:
                logger.exception(e)
                logger.exception(self.data['paths'][path][method]['requestBody']['content'])
                raise e

    def get_supported_method(self, path: str) -> List:
        """获取path支持的请求类型"""
        return list(self.data["paths"][path].keys())

    def get_supported_content_type(self, path: str) -> List:
        """获取path支持的content—type"""
        for method in self.get_supported_method(path):
            yield list(self.data['paths'][path][method]["requestBody"]["content"].keys())

    @classmethod
    def get_value(cls, obj: dict, field: str = ''):
        field_found = []
        for key, value in obj.items():
            if field == key:
                field_found.append(value)
            elif isinstance(value, dict):
                results = cls.get_value(value, field)
                field_found.extend(results)
            elif isinstance(value, list):
                for component in value:
                    if isinstance(component, dict):
                        list_results = cls.get_value(component, field)
                        field_found.extend(list_results)
            else:
                continue
        return field_found

    def dump(self):
        for path in self.data['paths'].keys():
            for method in self.data['paths'][path].keys():
                for content_type in self.data['paths'][path][method]["requestBody"]["content"].keys():
                    schema = self.data['paths'][path][method]['requestBody']['content'][content_type].get('schema', None)


if __name__ == '__main__':
    swagger_parser = SwaggerParser(r'/Users/heweidong/PycharmProjects/AutoTest/src/swagger/Swagger_Api_综合管理平台.json')
    # print(swagger_parser.get_param_schema('/api/v2/topo/icon/', 'post'))
    print(swagger_parser.data['paths'][r'/api/v2/auditor/device/{id}/un_register/']['post']['responses'])
    # print(get_brief_info(paths))
    # paths = swagger_json.get("paths")
    # print(get_request_info(paths, '/api/v2/topo/icon/'))
    # combine_map = get_combination_map(paths)
    # print(combine_map['/api/v2/auditor/device/{id}/un_register/'][0])
    # len(swagger_json.get("paths").keys())
    # print(swagger_json.get("paths").get(swagger_json.get("paths").keys().__next__))
    ...




