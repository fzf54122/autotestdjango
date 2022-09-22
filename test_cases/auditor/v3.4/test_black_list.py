import time
from unittest import TestCase
import unittest
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.core.assertion import JsonPathExtractStrategy
from settings import host
import shortuuid
from utils.core.decorators import depends_on
from datetime import date, datetime, timedelta
from settings import supported_protocols

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestBlackList(TestCase):
    session = None

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.rule_name = shortuuid.ShortUUID().random(length=20)

    def list_blacklist(self):
        data = {
            'page': 1,
            'type': None,
            'page_size': 20
        }
        response = self.session.request('GET', url=f'https://{host}/v2/black-list/', params=data)
        return response

    def test_get_list(self):
        response = self.list_blacklist()
        self.assertEqual(response.status_code, 200)

    def test_enable_all(self):
        enable_params = {
            "is_active": "true"
        }
        response = self.session.request('PUT', url=f'https://{host}/v2/black-list/', json=enable_params)
        self.assertEqual(response.status_code, 200)

    @depends_on('test_enable_all')
    def test_disable_all(self):
        disable_params = {
            "is_active": "false"
        }
        response = self.session.request('PUT', url=f'https://{host}/v2/black-list/', json=disable_params)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
