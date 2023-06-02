#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 下午4:57
# @Author  : fzf
# @File    : test_object_time.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *
from utils.setting import FirewallOperatorPwd, FirewallOperator


class TestObjectTime(TestCase):
    """
    对象管理：时间对象
    """
    session = None
    tags = ['test']
    versions = ['3.2']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username=FirewallOperator, password=FirewallOperatorPwd)
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
        """
        对象管理：时间对象-添加
        """
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
                    "start_time": "00:00:00",
                    "end_time": "23:59:59"
                }
            ]
        }
        response = self.session.post(url='v1/period/', json=payload)
        self.assertEqual(response.status_code, 201)
        ids = self.strategy.extract(response, '$.id')
        self.cache_map['object_id'] = ids[0]

    @depends_on('test_add_time_object')
    def test_detail_view(self):
        """
        对象管理：时间对象-详情
        """
        response = self.session.get(url='v1/period/{}'.format(self.cache_map['object_id']))
        self.assertEqual(response.status_code, 200)

    @depends_on('test_detail_view')
    def test_object_delete(self):
        """
        对象管理：时间对象-删除
        """
        response = self.session.delete(url='v1/period/{}'.format(self.cache_map['object_id']))
        try:
            self.assertEqual(response.status_code, 204)
        except AssertionError as e:
            print('Response: {}'.format(response.text))
            raise e

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
