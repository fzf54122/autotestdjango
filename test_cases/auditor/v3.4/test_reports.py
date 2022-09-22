import random
import time
from unittest import TestCase
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.core.assertion import JsonPathExtractStrategy
from settings import host
import shortuuid
from utils.core.decorators import depends_on
from datetime import date, datetime, timedelta
from settings import supported_protocols
from utils.generator import IPv4Strategy, MACAddressStrategy
import random

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestReports(TestCase):
    session = None
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache: dict = {}

    def test_export_setting(self):
        payload = {
            "is_day_enabled": 'true',
            "is_week_enabled": 'true',
            "is_month_enabled": 'true',
            "categories": [5, 6, 7]
        }
        response = self.session.request('PATCH', url=f'https://{host}/v2/home/reports-export-setting/', json=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
