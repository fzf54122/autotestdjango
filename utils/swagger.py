from typing import List, Any, Dict
import re
from pydantic import BaseModel, validator
from jsonpath_ng import parse
from pydantic.types import Json

# TODO: 暂时搁置，各个项目的swagger格式不一致，有的用的schema有的用的content，适配起来工作量太高，先留着后续再考虑
# 因此swagger目前只做到可以把path导入就行，至于数据生成什么的暂时不考虑


class Swagger(BaseModel):
    """swagger 接口对象"""
    version: str = '2.0'
    base_path: str = "/api/v2"
    host: str = ""
    apis: List = []
    folders: Any = None
    base_params: Any = None
    options: Dict = {'base_path': True, 'host': True}

    def search_json_dict(self, content: Dict, key):
        if key in content.keys():
            return content[key]

        for k, v in content.items():
            if isinstance(v, dict):
                return self.search_json_dict(v, key)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        return self.search_json_dict(item, key)

    def validate(self, content: Dict):
        # 版本设置
        if "swagger" in content.keys():
            if content.get('swagger', None) != '2.0':
                raise AttributeError('Must swagger must be 2.0')
            else:
                self.version = '2.0'
        if "openapi" in content.keys():
            self.version = '3.0'
        if "swagger" not in content.keys() and "openapi" not in content.keys():
            raise AttributeError('Must contain a swagger field 2.0 or 3.0')
        return True

    def set_base_path(self, content: Dict):
        """设置基础路径"""
        if 'basePath' in content.keys():
            self.base_path = content['basePath']
        else:
            raise AttributeError('Must contain a basePath')

    def _search_by_ref(self, ref: str, content: Dict):
        """查找ref的引用对象，通过转换成jsonpath实现"""
        ref_regex = re.compile(r"^\#(\/\S+)+$")
        if ref_regex.match(ref):
            json_path = ref.replace('#', '$').replace(r'/', '.')
            jp = parse(json_path)
            matches = jp.find(content)
            res = [match.value for match in matches]
            if len(res) == 0:
                raise ValueError("Could not find ref value, check path")
            else:
                return res[0]
        else:
            raise ValueError('ref format invalid, please check')

    def set_apis(self, content: Dict):
        methods: set = {'get', 'post', 'put', 'delete', 'patch'}
        containers: List = []
        if 'paths' not in content.keys():
            raise AttributeError('content must contains paths field')
        for api in content['paths']:
            supported_methods = list(methods & set(api.keys()))
            for method in supported_methods:
                ...


if __name__ == '__main__':
    # ref_regex = re.compile(r"^\#(\/\S+)+$")
    # info = {'title': "态势感知", 'description': "态势感知文档描述", 'version': "v2", 'param': ['1', '2']}
    # res = Swagger().search_json_dict(info, '1')
    # $ref: "#/definitions/IPAddress"
    ...



