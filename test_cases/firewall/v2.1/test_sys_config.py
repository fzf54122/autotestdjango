from unittest import TestCase
import unittest
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on
import inspect


class TestSysConfig(TestCase):
    session = None
    tag = ['test']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='admin', password='Admin@123')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_product_info(self) -> None:
        response = self.session.request('GET', url='/v1/setting/product/')
        self.assertEqual(response.status_code, 200)

    def test_status(self) -> None:
        response = self.session.get('/v1/setting/status/')
        self.assertEqual(response.status_code, 200)

    def test_enable_self_check(self) -> None:
        payload = {
            'valid': 'true'
        }

        response = self.session.put('v1/setting/selfcheck/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_network_config(self) -> None:
        response = self.session.get('/v1/setting/ip/')
        self.assertEqual(response.status_code, 200)

    def test_enable_proxy(self) -> None:
        payload = {
            'active': 'true'
        }
        response = self.session.patch('v1/setting/snmp/proxy/', json=payload)
        self.assertEqual(response.status_code, 200)

    @depends_on('test_enable_proxy')
    def test_snmp_config(self) -> None:
        payload = {
            "id": 1,
            "versions": [
                1,
                2,
                3
            ],
            "trap": "10.30.3.223",
            "group": "public"
        }
        response = self.session.patch('v1/setting/snmp/config/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_ntp_config(self):
        response = self.session.get('v1/setting/ntp/')
        self.assertEqual(response.status_code, 200)

    def test_usage(self):
        response = self.session.get('v1/setting/usage/')
        self.assertEqual(response.status_code, 200)

    def test_custom_storage_config(self):
        response = self.session.get('v1/setting/storage/custom/')
        self.assertEqual(response.status_code, 200)
        payload = {
            "id": 1,
            "disk_total": "905.97GB",
            "extend_disk_total": 927713.71,
            "unused_percent": "98%",
            "log_size": "452.99 GB",
            "report_size":"452.99 GB",
            "log": 50,
            "report": 50
        }
        response = self.session.put('v1/setting/storage/custom/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_report_storage_config(self):
        response = self.session.get('v1/setting/storage/report/')
        self.assertEqual(response.status_code, 200)

    def test_syslog_settings(self):
        response = self.session.get('v1/setting/syslog/')
        self.assertEqual(response.status_code, 200)
        payload = {
            "valid": 'true',
            "protocol": "UDP",
            "address": "10.30.3.223",
            "port": 514
        }
        response = self.session.put('v1/setting/syslog/', json=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
