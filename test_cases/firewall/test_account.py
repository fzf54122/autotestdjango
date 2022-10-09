from unittest import TestCase
import unittest
from utils.core.test_core import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on


class TestAccount(TestCase):
    session = None
    tags = ['test']
    versions = ['2.1']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='admin', password='Admin@123')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_create_operator(self) -> None:
        password_cipher = CipherFactory.create_cipher('firewall/password')
        data = {
            'username': 'test666',
            'password1': password_cipher.encrypt('Bl666666'),
            'password2': password_cipher.encrypt('Bl666666'),
            'group': 'Operator',
            'description': '',
            'auth_type': 0,
            'is_active': 'true'
        }
        response = self.session.request('POST', url='/v1/user/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '1005')

    @depends_on('test_create_operator')
    def test_create_auditor(self):
        password_cipher = CipherFactory.create_cipher('firewall/password')
        data = {
            'username': 'test999',
            'password1': password_cipher.encrypt('Bl666666'),
            'password2': password_cipher.encrypt('Bl666666'),
            'group': 'Auditor',
            'description': '',
            'auth_type': 0,
            'is_active': 'true'
        }
        response = self.session.request('POST', url=f'/v1/user/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '1005')

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
