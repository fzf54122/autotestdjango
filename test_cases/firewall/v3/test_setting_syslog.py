#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 上午9:30
# @Author  : fzf
# @File    : test_setting_syslog.py
# @Software: PyCharm
import unittest
from typing import Any
from unittest import TestCase

from utils.setting import *
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *


class TestSettingLogin(TestCase):
    """
    系统设置：SYSLOG
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

    def test_bind_syslog(self) -> None:
        """
        系统设置：SYSLOG-绑定
        """
        payload = {"valid": True, "protocol": "TCP", "address": SYSLogServer, "port": 512}
        response = self.syslog(payload)
        self.assertEqual(response.get("address"), payload.get("address"))

    @depends_on("test_syslog")
    def test_remove_syslog(self) -> None:
        """
        系统设置：SYSLOG-解邦
        """
        payload = {"valid": False, "protocol": "TCP", "address": "", "port": None}
        response = self.syslog(payload)
        print("stoping")
        self.assertEqual(response.get("valid"), False)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()

    def syslog(self, _payload) -> Any:
        payload = {"valid": True, "protocol": "TCP", "address": "", "port": None}
        payload.update(_payload)
        response = self.session.put(url="/v1/setting/syslog/", json=payload).json()
        return response


if __name__ == '__main__':
    unittest.main()
