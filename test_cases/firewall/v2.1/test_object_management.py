from unittest import TestCase
import unittest
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
# from settings import host
from utils.core.decorators import depends_on
import inspect

from utils.log import get_logger

logger = get_logger(__name__)


class TestObjectManagement(TestCase):
    session = None
    tag = ['test']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache_map = {}

    def test_list_object(self):
        payload = {
            'name': None,
            'cycle[0]': None,
            'cycle[1]': None,
            'start_datetime': None,
            'end_datetime': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/period', params=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_time_object(self):
        payload = {
            "name": "all",
            "start_datetime": None,
            "end_datetime": None,
            "repeat": [
                {
                    "weekdays": [
                        1,
                        2,
                        3,
                        4,
                        7,
                        6,
                        5
                    ],
                    "start_time":"00:00:00",
                    "end_time":"23:59:59"
                }
            ]
        }
        response = self.session.post(url='v1/period/', json=payload)
        self.assertEqual(response.status_code, 201)
        ids = self.strategy.extract(response, '$.id')
        self.cache_map['object_id'] = ids[0]

    @depends_on('test_add_time_object')
    def test_detail_view(self):
        response = self.session.get(url='v1/period/{}'.format(self.cache_map['object_id']))
        self.assertEqual(response.status_code, 200)

    @depends_on('test_detail_view')
    def test_object_delete(self):
        response = self.session.delete(url='v1/period/{}'.format(self.cache_map['object_id']))
        try:
            self.assertEqual(response.status_code, 204)
        except AssertionError as e:
            print('Response: {}'.format(response.text))
            raise e

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()
