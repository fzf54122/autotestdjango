from unittest import TestCase
import unittest
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on
import inspect


class TestEventManagement(TestCase):
    session = None
    tag = ['test']
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

    def test_list_event(self):
        payload = {
            'src_ip': None,
            'dst_ip': None,
            'start_time': None,
            'end_time': None,
            'type': None,
            'protocol': None,
            'action': None,
            'is_read': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/sec-event', params=payload)
        self.assertEqual(response.status_code, 200)
        ids = self.strategy.extract(response, '$.results.[0].id')
        if len(ids) == 1:
            self.cache_map['sec_event_id'] = ids[0]

    @depends_on('test_list_event')
    def test_sec_event_detail(self):
        if 'sec_event_id' in self.cache_map:
            sec_event_id = self.cache_map['sec_event_id']
            response = self.session.get(f'v1/sec-event/{sec_event_id}')
            self.assertEqual(response.status_code, 200)
        else:
            self.assertTrue(True)

    def test_list_sys_event(self):
        payload = {
            'content': None,
            'level': None,
            'category': None,
            'classification': None,
            'is_read': None,
            'start_time': None,
            'end_time': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/sys-event/', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_list_fault_packet(self):
        payload = {
            'ip': None,
            'mac': None,
            'start_time': None,
            'end_time': None,
            'protocol': None,
            'ipver': None,
            'is_read': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/audit/fault_packet', params=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()
