#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午4:10
# @Author  : fzf
# @File    : test_policy_industry.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperator, FirewallOperatorPwd, Policy_SIP, Policy_DIP


@ddt
class TestPolicyIndustry(TestCase):
    """
    安全策略：工业协议
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

    @list_data(
        [
            {"action": "alert"},
            {"action": "drop"},
            {"action": "pass"},
            {"protocol": "ADS/AMS", "args": {"function_code": 5}, "extra_data": "{\"displayMap\":{\"function_code\":\"5-ADS Write Control\"},\"selectItemsIdMap\":{\"function_code\":2177}}"}
        ]
    )
    def test_industry_add(self, data):
        """
        安全策略：工业协议-添加
        """
        payload = {
            "action": "alert",
            "active": True,
            "args": {"function_code": 4},
            "dst": Policy_DIP,
            "extra_data": "{\"displayMap\":{\"function_code\":\"4-ADS Read State\"},\"selectItemsIdMap\":{\"function_code\":2176}}",
            "function_code": "4",
            "name": shortuuid.ShortUUID().random(length=20),
            "protocol": "ADS/AMS",
            "smac": None,
            "src": Policy_SIP,
        }
        payload.update(data)
        response = self.session.post(url="/v1/policy/industry", json=payload)
        self.assertEqual(201, response.status_code)

    def test_industry_del(self):
        """
        安全策略：工业协议-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/industry/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/industry/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
