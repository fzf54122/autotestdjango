import random
from unittest import TestCase

import shortuuid

from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *
from utils.core.test_core import ddt, list_data


@ddt
class TestBasicPolicy(TestCase):
    session = None
    tags = ['test']
    versions = ['2.3']
    host = '10.30.6.66'

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache_map = {}

    def test_list_firewall_mode(self):
        response = self.session.get('v1/policy/')
        self.assertEqual(response.status_code, 200)

    def _set_work_mode(self):
        payload = {
            "mode": "work",
            "default_drop": True,
            "dpi": True,
            "flow_detect": True,
            "black_detect": True
        }
        self.session.put('v1/policy/', json=payload)

    def test_config_firewall_mode(self):
        payload = {
            "mode": random.choice(["test", "study", "work"]),
            "default_drop": random.choice([True, False]),
            "dpi": random.choice([True, False]),
            "flow_detect": random.choice([True, False]),
            "black_detect": random.choice([True, False])
        }
        response = self.session.put('v1/policy/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_list_basic_policy(self):
        payload = {
            'smac': None,
            'sip': None,
            'sport': None,
            'dip': None,
            'dport': None,
            'protocol': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/basic', params=payload)
        self.assertEqual(response.status_code, 200)

    @list_data(
        [
            {'action': 'pass'},
            {'action': 'alert'},
            {'action': 'drop'},
            {'protocol': 'ICMP'},
            {'protocol': 'TCP', "state": ["New", "Established", "Invalid", "Related"]},
            {'protocol': 'HTTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 80},
            {'protocol': 'FTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 21},
            {'protocol': 'POP3', "state": ["New", "Established", "Invalid", "Related"], 'dport': 110},
            {'protocol': 'Telnet', "state": ["New", "Established", "Invalid", "Related"], 'dport': 23},
            {'protocol': 'SMTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 25},
            {'protocol': 'DNS(TCP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 53},
            {'protocol': 'DNS(UDP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 53},
            {'protocol': 'TFTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 69},
            {'protocol': 'HTTPS', "state": ["New", "Established", "Invalid", "Related"], 'dport': 443},
            {'protocol': 'SNMP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 161},
            {'protocol': 'SNMP(trap)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 161},
            {'protocol': 'H323(RAS)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 1719},
            {'protocol': 'H323(Q931)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 1720},
            {'protocol': 'RTSP(UDP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 554},
            {'protocol': 'RTSP(TCP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 554},
        ]
    )
    def test_add_policy(self, data):
        self._set_work_mode()
        payload = {
            "name": shortuuid.ShortUUID().random(length=20),
            "sip": "",
            "dip": "",
            "smac": None,
            "sport": None,
            "dport": None,
            "protocol": "ALL",
            "action": "alert",
            "active": True,
            "state": None,
            "time_object": None
        }
        payload.update(data)
        response = self.session.post(url='v1/policy/basic/', json=payload)
        try:
            self.assertEqual(response.status_code, 201)
        except AssertionError as e:
            error = self.strategy.extract(response, '$.error')
            if len(error) == 1:
                self.assertEqual(error[0], '1111')
            else:
                raise e

    @depends_on('test_add_policy')
    def test_delete_policy(self):
        payload = {
            'smac': None,
            'sip': None,
            'sport': None,
            'dip': None,
            'dport': None,
            'protocol': None,
            'action': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/basic', params=payload)
        ids = self.strategy.extract(response, '$.results.id')
        for _id in ids:
            response = self.session.delete('v1/policy/basic/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
            {'active': True},
            {'active': False},
    ])
    def test_config_all(self, data):
        payload = {
            'active': True
        }
        payload.update(data)
        params = {
            'smac': None,
            'sip': None,
            'sport': None,
            'dip': None,
            'dport': None,
            'protocol': None,
            'action': None,
            'active': None
        }
        response = self.session.patch('v1/policy/basic', params=params, json=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()
