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

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestThreshold(TestCase):
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

    def test_modify_threshold(self):
        payload = {
            "lockout_threshold": 5,
            "lockout_duration": 30,
            "login_timeout_duration": 18,
            "dev_offline_timeout": 3,
            "cpu_alert_percent": 80,
            "disk_alert_percent": 80,
            "disk_clean_percent": 80,
            "log_retention_limit": 6,
            "log_auto_remove_limit": 7,
            "if_rate_ave_range_percent": 1,
            "if_rate_threshold": 1024,
            "if_rate_zero": 5,
            "protocol_alert": 'true'
        }

        response = self.session.request('PUT', url=f'/v2/setting/threshold/', json=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
