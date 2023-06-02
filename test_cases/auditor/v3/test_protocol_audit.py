import time
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestProtocolAudit(TestCase):
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
            'ip': None,
            'mac': None,
            'port': None,
            'l4_protocol': None,
            'protocol': None,
            'ordering': None,
            'start_time': None,
            'end_time': None,
            'page_size': 20,
            'time': None
        }
        response = self.session.request('GET', url=f'/v2/packet/', params=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
