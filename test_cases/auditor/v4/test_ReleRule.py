#!/usr/bin/ python3
# -*- coding: utf-8 -*-
"""
@Project ：autotestdjango 
@File ：test_account.py
@Author ：fzf
@Date ：2023/1/9 上午10:25 
"""

import unittest
from unittest import TestCase

from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestRule(TestCase):
    session = None
    tags = ['test']
    versions = ['4.2']
    host = '10.30.5.99'

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='fzf002', password='admin123')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = cls.host
        cls.session.NewLogin(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_CreateReleRule(self) -> None:
        payload = {
            'category': 1,
            'freq': 10,
            'level': 1,
            'name': f"fzf002",
            'order_by': 1,
            'result': "ssss",
            'rules': [{'ro_list': [{'key': "category", 'value': 2, 'oper': "=="}], 'count': 2, 'oper': "&&"}],
            'status': 1
        }
        response = self.session.request('POST', url="/v2/strategy_center/api/correlation", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_CreateCustomProtocol(self) -> None:
        payload = {
            "dst_ip": None,
            "dst_port": None,
            "is_active": False,
            "name": "fzf0013",
            "protocol_type": 0,
            "rule": [
                {"type": "string", "offset": 1, "length": 2, "value": f"1213123123123322222", "value_type": "hex"}],
            "src_ip": None,
            "src_port": None,
        }
        response = self.session.request('POST', url="/v2/strategy_center/api/custom_protocol", json=payload)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        ...


if __name__ == '__main__':
    unittest.main()
