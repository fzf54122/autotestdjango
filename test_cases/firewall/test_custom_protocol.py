import random
from unittest import TestCase
import unittest
from utils.core.test_core import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on
import inspect
from utils.core.test_core import ddt, list_data
import shortuuid


@ddt
class TestCustomProtocol(TestCase):
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

    def test_list_custom_protocol(self):
        payload = {
            'name': None,
            'src_ip': None,
            'dst_ip': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/custom', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_protocol(self):
        self._set_work_mode()
        payload = {
            "name": shortuuid.ShortUUID().random(length=10),
            "protocol": "TCP",
            "src_ip": "",
            "dst_ip": "",
            "src_port": None,
            "dst_port": None,
            "time_object": None,
            "action": "alert",
            "active": True,
            "features": [
                {
                    "match_type": 1,
                    "byte_offset": "0",
                    "byte_width": "2",
                    "byte_feature": "0000",
                    "feature_type": "hex"
                }
            ]
        }
        response = self.session.post(url='v1/policy/custom/', json=payload)
        self.assertEqual(response.status_code, 201)

    @depends_on('test_add_protocol')
    def test_delete_protocol(self):
        payload = {
            'name': None,
            'src_ip': None,
            'dst_ip': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/custom', params=payload)
        ids = self.strategy.extract(response, '$.results.id')
        for _id in ids:
            self.session.delete('v1/policy/custom/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {'active': True},
        {'active': False},
    ])
    def test_config_all(self, data):
        payload = data
        params = {
            'name': None,
            'src_ip': None,
            'dst_ip': None,
            'action': None,
            'active': None,
        }
        response = self.session.patch('/v1/policy/custom', params=params, json=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()
