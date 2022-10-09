import time
from unittest import TestCase
from utils.core.test_core import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.core.assertion import JsonPathExtractStrategy
import shortuuid
from utils.core.decorators import depends_on
from datetime import date, datetime, timedelta
from settings import supported_protocols
from utils.generator import IPv4Strategy, MACAddressStrategy

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestDevice(TestCase):
    session = None
    host = ''
    tags = ['test']
    versions = ['3.4']

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.rule_name = shortuuid.ShortUUID().random(length=15)

    def list_device(self):
        data = {
            'page': 1,
            'type': None,
            'search': None,
            'page_size': 20
        }
        response = self.session.request('GET', url=f'/v2/device/', params=data)
        return response

    def test_get_list(self):
        response = self.list_device()
        self.assertEqual(response.status_code, 200)

    def test_create_device(self):

        data = {
            "name": self.rule_name,
            "category": "通讯设备",
            "ip": IPv4Strategy().handle(area='private'),
            "mac": MACAddressStrategy().handle().upper(),
            "ip_mac_bond": 'false',
            "value": 1,
            "description": ""
        }

        response = self.session.request('POST', url=f'/v2/device/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertIn(message[0], ['已存在相同名称的设备', '已存在相同IP的设备'])

    @depends_on('test_create_device')
    def test_delete_device(self):
        search_data = {
            'page': 1,
            'type': None,
            'search': self.rule_name,
            'page_size': 100
        }
        response = self.session.request('GET', url=f'/v2/device/', params=search_data)
        rule_id = self.strategy.extract(response, '$.results.[0].id')[0]
        response = self.session.request('DELETE', url=f'/v2/device/{rule_id}/')
        self.assertEqual(response.status_code, 204)

    def check_learning_status(self):
        response = self.session.request('GET',  url=f'/v2/device/learned/is_learning/')
        status = self.strategy.extract(response, '$.status')
        if len(status) == 0:
            logging.error(f"detect status error, response: {response.json()}")
            raise ValueError('响应内容异常，未提取到status字段')
        return status[0]

    def test_device_learning(self):
        start_params = {
            "start_time": datetime.now().strftime(TIME_FORMAT),
            "end_time": (datetime.now() + timedelta(minutes=5)).strftime(TIME_FORMAT),
            "ip_range": None,
            'include_ipv6': 'false'
        }
        response = self.session.request('POST', url=f'/v2/device/study/start/', json=start_params)
        self.assertEqual(response.status_code, 200)

        while self.check_learning_status() != 0:
            time.sleep(1)
        else:
            response = self.session.request('POST', url=f'/v2/device/learned/')
            self.assertEqual(response.status_code, 200)

    def test_enable_all(self):
        enable_params = {
            'ip_mac_bond': 'true'
        }
        response = self.session.request('PUT', url=f'/v2/device/', json=enable_params)
        self.assertEqual(response.status_code, 200)

    @depends_on('test_enable_all')
    def test_disable_all(self):
        disable_params = {
            'ip_mac_bond': 'false'
        }
        response = self.session.request('PUT', url=f'/v2/device/', json=disable_params)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
