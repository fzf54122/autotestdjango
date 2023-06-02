import time
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestRuntimeInspect(TestCase):
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

    def test_exterior(self):
        response = self.session.request('GET', url=f'/v2/setting/exterior/')
        self.assertEqual(response.status_code, 200)

    def test_dev_traffic_stats(self):
        payload = {
            'interval': 10,
            'direction': 0,
            'span': 5
        }
        response = self.session.request('GET', url=f'/v2/home/dev-traffic-stat/', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_nic_traffic_line_chart(self):
        payload = {
            'interval': 10,
            'span': 5
        }
        response = self.session.request('GET', url=f'/v2/home/nic-traffic-line-chart/', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_proto_traffic_stat(self):
        payload = {
            'interval': 10,
            'span': 5
        }
        response = self.session.request('GET', url=f'/v2/home/proto-traffic-stat/', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_sys_stat(self):
        payload = {
            'interval': 10,
            'span': 5
        }
        response = self.session.request('GET', url=f'/v2/home/sys-stat/', params=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
