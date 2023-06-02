#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 上午11:12
# @Author  : fzf
# @File    : test_available_bypass.py
# @Software: PyCharm
import unittest
from typing import Any
from unittest import TestCase
from utils.setting import FirewallOperator,FirewallOperatorPwd
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestAvailableBypass(TestCase):
    """
    高可用性-ByPass开启和关闭
    """
    session = None
    tags = ['test']
    versions = ['3.2']
    host = '10.30.6.165'

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username=FirewallOperator, password=FirewallOperatorPwd)
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def Bypass(self, status: bool) -> Any:
        payload = {
            "active": status,
        }
        return self.session.put(url="/v1/network/available/bypass/", json=payload).json()

    def test_bypass(self):
        """
        开启Bypass
        """
        response = self.Bypass(True)
        self.assertEqual(response.get("active"), True)

    def test_bypass_remove(self):
        """
        关闭Bypass
        """
        response = self.Bypass(False)
        self.assertEqual(response.get("active"), False)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
