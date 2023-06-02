#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午4:56
# @Author  : fzf
# @File    : test_policy_white.py
# @Software: PyCharm
import time
import unittest
from datetime import datetime, timedelta
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.setting import FirewallOperatorPwd, FirewallOperator

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class TestPolicyWhite(TestCase):
    """
    安全策略：白名单策略
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

    def test_list_whitelist(self):
        payload = {
            'ip': None,
            'port': None,
            'protocol': None,
            'transport': None,
            'active': None,
            'page': 1,
            'page_size': 20
        }
        response = self.session.get('v1/policy/white', params=payload)
        self.assertEqual(response.status_code, 200)

    def _get_whitelist_learning_state(self):
        response = self.session.get('v1/policy/white/study/')
        state = self.strategy.extract(response, '$.state')
        if len(state) == 1:
            return state[0]
        else:
            raise ValueError('StateError: not found')

    def test_whitelist_learning(self):
        """
        安全策略：白名单策略-自学习
        """
        payload = {
            "start_time": datetime.now().strftime(TIME_FORMAT),
            "end_time": (datetime.now() + timedelta(minutes=5)).strftime(TIME_FORMAT),
            "network": None,
            "protocols": [
                "HTTP",
                "FTP",
                "TFTP",
                "POP3",
                "Telnet",
                "SMTP",
                "DNS",
                "SNMP",
                "SNMP(trap)",
                "Modbus",
                "S7COMM",
                "DNP3",
                "FINS",
                "OpcUA",
                "OpcDA",
                "OpcAE",
                "S7COMM-PLUS",
                "Profinet",
                "IEC61850/GOOSE",
                "IEC61850/MMS",
                "IEC61850/SV",
                "IEC104",
                "BACnet"
            ]
        }
        response = self.session.post('v1/policy/white/study/', json=payload)
        self.assertEqual(response.status_code, 201)
        time_count = 360
        while self._get_whitelist_learning_state() == 'STARTED' and time_count > 0:
            time.sleep(1)
            time_count -= 1
        else:
            self.assertNotEqual(self._get_whitelist_learning_state(), 'STARTED')

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()


