from unittest import TestCase

from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestHomePage(TestCase):
    session = None
    tags = ['test']
    versions = ['2.1']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_traffic_rate(self):
        response = self.session.get('v1/home/traffic-rate/')
        self.assertEqual(response.status_code, 200)

    def test_usage(self):
        response = self.session.get('v1/home/usage/')
        self.assertEqual(response.status_code, 200)

    def test_home_product(self):
        response = self.session.get('v1/home/product/')
        self.assertEqual(response.status_code, 200)

    def test_home_event(self):
        response = self.session.get('v1/home/event/')
        self.assertEqual(response.status_code, 200)

    def test_home_traffic_state(self):
        payload = {
            'hours': 1
        }
        response = self.session.get('v1/home/traffic-stat', params=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()