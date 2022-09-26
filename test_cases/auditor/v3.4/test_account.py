from unittest import TestCase
import unittest
from utils.core.test_core import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on
import inspect


class TestAccount(TestCase):
    session = None
    tag = ['test']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='admin', password='Admin@123')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_create_engineer(self) -> None:
        password_cipher = CipherFactory.create_cipher('auditor/password')
        data = {
            'username': 'test666',
            'password1': password_cipher.encrypt('Bl666666'),
            'password2': password_cipher.encrypt('Bl666666'),
            'groups': 'Engineer',
            'description': None
        }
        response = self.session.request('POST', url='/v2/user/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '用户名已存在')

    @depends_on('test_create_engineer')
    def test_create_operator(self):
        password_cipher = CipherFactory.create_cipher('auditor/password')
        data = {
            'username': 'test999',
            'password1': password_cipher.encrypt('Bl666666'),
            'password2': password_cipher.encrypt('Bl666666'),
            'groups': 'Operator',
            'description': None
        }
        response = self.session.request('POST', url=f'/v2/user/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '用户名已存在')

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
