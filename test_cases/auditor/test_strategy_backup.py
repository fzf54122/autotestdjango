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


class TestStrategyBackUp(TestCase):
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

    def test_modify_cron(self):
        payload = {
            "is_day_enabled": 'true',
            "is_week_enabled": 'false',
            "is_month_enabled": 'false'
        }

        response = self.session.request('PATCH', url=f'/v2/strategy/strategy-backup-export-setting/',
                                        json=payload)
        self.assertEqual(response.status_code, 200)

    def test_backup_strategy(self):
        response = self.session.request('POST', url=f'/v2/strategy/backups/')
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    current_time = time.time()
