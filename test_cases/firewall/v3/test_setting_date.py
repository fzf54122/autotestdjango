#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 下午3:44
# @Author  : fzf
# @File    : test_setting_date.py
# @Software: PyCharm
import time
import unittest
from typing import Any

from unittest import TestCase
from datetime import datetime
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.setting import FirewallOperatorPwd, FirewallOperator, NTPServer


class TestSettingDate(TestCase):
    """
    NTP时间：valid：True
    手动设置时间：valid：False
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

    def test_bind_date(self) -> None:
        """
        系统设置：时间设置-手动设置时间
        """
        payload = {"valid": False, "time": "2023-05-31 16:27:00", "address": None}
        response = self.NTP(_payload=payload)
        self.assertEqual(response.get("address"), payload.get("address"))

    def test_bind_ntp(self) -> None:
        """
        系统设置：时间设置-NTP
        """
        payload = {"valid": True, "time": None, "address": NTPServer}
        response = self.NTP(_payload=payload)
        self.assertEqual(response.get("valid"), True)
        self.assertEqual(response.get("address"), payload.get("address"))

    def NTP(self, _payload) -> Any:
        payload = {"valid": False, "time": "", "address": ""}
        payload.update(_payload)
        response = self.session.put(url="v1/setting/ntp/", json=payload).json()
        return response

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
