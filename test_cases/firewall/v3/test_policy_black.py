#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:29
# @Author  : fzf
# @File    : test_policy_black.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperatorPwd, FirewallOperator


@ddt
class TestPolicyBlack(TestCase):
    """
    安全策略：黑名单策略
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

    @list_data([
        {"active": True},
        {"active": False}
    ])
    def test_number_single_status(self, data):
        """
        安全策略：黑名单策略-切换动作
        """
        payload = {
            "active": True
        }
        payload.update(data)
        response = self.session.patch(url="v1/policy/black/{}/".format(1), json=payload)
        self.assertEqual(200, response.status_code)

    @list_data([
        {"action": "drop"},
        {"action": "alert"}
    ])
    def test_number_single_action(self, data):
        """
        安全策略：黑名单策略-切换状态
        """
        payload = {
            "active": True
        }
        payload.update(data)
        response = self.session.patch(url="v1/policy/black/{}/".format(1), json=payload)
        self.assertEqual(200, response.status_code)

    @list_data([
        {"action": "drop"},
        {"action": "drop"},
        {"active": True},
        {"active": False}
    ])
    def test_reset(self, data):
        """
        安全策略：黑名单策略-全部开启或切换动作
        """
        params = {
            "search": None,
            "source": None,
            "level": None,
            "action": None,
            "active": None,
        }
        payload = {
            # "action": None,
            # "active": None,
        }
        payload.update(data)
        response = self.session.patch(url="v1/policy/black/", params=params, json=payload)
        self.assertEqual(200, response.status_code)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
