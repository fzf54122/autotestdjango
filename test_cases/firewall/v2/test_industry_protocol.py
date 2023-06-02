from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *
from utils.core.test_core import ddt, list_data


@ddt
class TestIndustryProtocol(TestCase):
    session = None
    tags = ['test']
    versions = ['2.1']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache_map = {}

    def _set_work_mode(self):
        payload = {
            "mode": "work",
            "default_drop": True,
            "dpi": True,
            "flow_detect": True,
            "black_detect": True
        }
        self.session.put('v1/policy/', json=payload)

    @list_data([
        {'modbus': False},
        {'modbus': True},
        {'s7': False},
        {'s7': True},
        {'dnp3': True},
        {'dnp3': False},
        {'fins': True},
        {'fins': False},
        {'opcua': False},
        {'opcua': True},
        {'opcda': False},
        {'opcda': True},
        {'opcae': False},
        {'opcae': True}
    ])
    def test_default_rule(self, data):
        payload = data
        response = self.session.patch('v1/policy/industry/default/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_list_modbus(self):
        payload = {
            'function_code': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/industry/modbus', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_modbus(self):
        payload = {
            "name": shortuuid.ShortUUID().random(length=20),
            "src": "192.168.0.1/24",
            "dst": "192.168.0.1/24",
            "smac": None,
            "function_code": 1,
            "action": "alert",
            "active": True,
            "args": {
                "start_address": None,
                "end_address": None,
                "length": None,
                "function_code": 1
            }
        }
        response = self.session.post('v1/policy/industry/modbus/', json=payload)
        self.assertEqual(response.status_code, 201)

    @depends_on('test_add_modbus')
    def test_delete_modbus_rule(self):
        payload = {
            'function_code': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/industry/modbus', params=payload)
        ids = self.strategy.extract(response, '$.results.[0].id')
        for _id in ids:
            response = self.session.delete('v1/policy/industry/modbus/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {'active': False},
        {'active': True}
    ])
    def test_config_all_modbus(self, data):
        payload = data
        params = {
            'function_code': None,
            'action': None,
            'active': None
        }
        response = self.session.patch('v1/policy/industry/modbus', json=payload, params=params)
        self.assertEqual(response.status_code, 200)

    def test_list_s7(self):
        payload = {
            'rosctr': None,
            'function_code': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/industry/s7', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_s7(self):
        payload = {
            "name": shortuuid.ShortUUID().random(length=20),
            "active": True,
            "action": "alert",
            "src": "192.168.0.1/24",
            "dst": "192.168.0.1/24",
            "smac": None,
            "args": {
                "rosctr": 3,
                "area": None,
                "min_value": None,
                "max_value": None,
                "function_code": 4
            }
        }
        response = self.session.post('v1/policy/industry/s7/', json=payload)
        self.assertEqual(response.status_code, 201)

    @depends_on('test_add_s7')
    def test_delete_s7(self):
        payload = {
            'rosctr': None,
            'function_code': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/industry/s7', params=payload)
        ids = self.strategy.extract(response, '$.results.[0].id')
        for _id in ids:
            response = self.session.delete('v1/policy/industry/s7/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {'active': False},
        {'active': True}
    ])
    def test_config_all_s7(self, data):
        payload = data
        params = {
            'rosctr': None,
            'function_code': None,
            'action': None,
            'active': None
        }
        response = self.session.patch('v1/policy/industry/s7', json=payload, params=params)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()
