import unittest
from unittest import TestCase

from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *
from utils.core.test_core import ddt

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


@ddt
class TestConnectionManagement(TestCase):
    session = None
    tags = ['test']
    versions = ['2.3']
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

    def test_list_connection(self):
        payload = {
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/connection', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_rule(self):
        payload = {
            "src": "192.168.0.1",
            "dst": "192.168.0.4",
            "speed": None,
            "count": "3",
            "active": True
        }
        response = self.session.post('v1/policy/connection', json=payload)
        self.assertEqual(response.status_code, 201)
        ids = self.strategy.extract(response, '$.id')
        self.assertEqual(len(ids), 1)
        self.cache_map['connection_rule_id'] = ids[0]

    # @list_data([
    #     {"active": False},
    #     {"active": True},
    # ])
    @depends_on('test_add_rule')
    def test_modify_enable_state(self):
        # payload = {"active": False}
        print(self.cache_map['connection_rule_id'])
        params = {'active': None}
        payload = {"active": True}
        # response = self.session.patch('v1/policy/connection/{}'.format(self.cache_map['connection_rule_id']), json=payload)
        response = self.session.patch('v1/policy/connection', json=payload, params=params)
        self.assertEqual(response.status_code, 200)

    @depends_on('test_modify_enable_state')
    def test_delete_rule(self):
        response = self.session.delete('v1/policy/connection/{}'.format(self.cache_map['connection_rule_id']))
        self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
