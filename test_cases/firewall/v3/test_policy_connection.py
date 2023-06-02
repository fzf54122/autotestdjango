#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:29
# @Author  : fzf
# @File    : test_policy_connection.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.core.test_core import list_data, ddt
from utils.setting import *
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestPolicyConnection(TestCase):
    """
    安全策略：连接管理
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
        {"speed": 1000},
        {"count": 1000}
    ])
    def test_policy_connection_add(self, data):
        """
        安全策略：连接管理-添加
        """
        payload = {"src": PolicyConnectSIP, "dst": PolicyConnectDIP, "speed": None, "count": None, "active": False}
        payload.update(data)
        response = self.session.post(url="v1/policy/connection/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_policy_connection_del(self):
        """
        安全策略：连接管理-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="v1/policy/connection/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/connection/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
