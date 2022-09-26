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
        response = self.session.request('PATCH', url=f'/v2/home/reports-export-setting/', json=payload)
        self.assertEqual(response.status_code, 200)

    def list_reports(self):
        payload = {
            'page': 1,
            'type': None,
            'search': None,
            'page_size': 20,
            'start_time': None,
            'end_time': None,
            'time[0]': None,
            'time[1]': None
        }
        response = self.session.get(url='/v2/home/reports', params=payload)
        return response

    def test_list_reports(self):
        response = self.list_reports()
        count = self.strategy.extract(response, '$.count')
        self.assertGreater(len(count), 0)
        self.assertEqual(response.status_code, 200)

    def test_download_report(self):
        list_response = self.list_reports()
        results = self.strategy.extract(list_response, '$.results')
        self.assertGreater(len(results), 0)
        results = results[0]
        finished_results = filter(lambda x: x['status'] == 1, results)


if __name__ == '__main__':
    current_time = time.time()
