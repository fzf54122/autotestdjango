import random
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
import random

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestLogAudit(TestCase):
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
        cls.cache: dict = {}

    def test_list_records(self):
        payload = {
            'page': 1,
            'search': None,
            'ordering': None,
            'start_time': None,
            'end_time': None,
            'page_size': 20,
            'time[0]': None,
            'time[1]': None
        }
        response = self.session.request('GET', url=f'/v2/packet/', params=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
