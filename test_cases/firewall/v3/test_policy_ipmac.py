#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:29
# @Author  : fzf
# @File    : test_policy_ipmac.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.setting import *
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestPolicyIPMAC(TestCase):
    """
    安全策略：IP/MAC
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

    def test_policy_IPMac_Add(self):
        """
        安全策略：IP/MAC-添加
        """
        payload = {
            "active": True,
            "ip": PolicyConnectSIP,
            "mac": "CC:D3:9D:97:65:31",
            "name": shortuuid.ShortUUID().random(length=20),
        }
        response = self.session.post(url="/v1/policy/ipmac/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_policy_IPMac_del(self):
        """
        安全策略：IP/MAC-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/ipmac/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/ipmac/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
