#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:30
# @Author  : fzf
# @File    : test_policy_protect.py
# @Software: PyCharm
import unittest
from unittest import TestCase
from utils.setting import *
from utils.core.test_core import ddt, list_data
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestPolicyProtect(TestCase):
    """
    安全策略：安全防护
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
        {"ddos": True,
            "flood": True,
            "icmp_big": 1,
            "icmp_big_threshold": 1500,
            "icmp_flood": 1,
            "icmp_flood_threshold": 10000,
            "icmp_scan": 1,
            "icmp_scan_threshold": 10000,
            "land": 1,
            "non_flood": 1,
            "scan": 1,
            "smurf": 1,
            "syn_flood": 1,
            "syn_flood_threshold": 10000,
            "tcp_scan": 1,
            "tcp_scan_threshold": 10000,
            "teardrop": 1,
            "udp_flood": 1,
            "udp_flood_threshold": 10000,
            "udp_scan": 1,
            "udp_scan_threshold": 10000,
            "winnuke": 1,},
        {"ddos": False,
         "flood": False,
         "icmp_big": 0,
         "icmp_big_threshold": 1500,
         "icmp_flood": 0,
         "icmp_flood_threshold": 10000,
         "icmp_scan": 0,
         "icmp_scan_threshold": 10000,
         "land": 0,
         "non_flood": 0,
         "scan": 0,
         "smurf": 0,
         "syn_flood": 0,
         "syn_flood_threshold": 10000,
         "tcp_scan": 0,
         "tcp_scan_threshold": 10000,
         "teardrop": 0,
         "udp_flood": 0,
         "udp_flood_threshold": 10000,
         "udp_scan": 0,
         "udp_scan_threshold": 10000,
         "winnuke": 0, },
    ])
    def test_policy_protect(self, data):
        """
        安全策略：安全防护-开启与关闭
        """
        payload = {
            "ddos": None,
            "flood": None,
            "icmp_big": 0,
            "icmp_big_threshold": 1500,
            "icmp_flood": 0,
            "icmp_flood_threshold": 10000,
            "icmp_scan": 0,
            "icmp_scan_threshold": 10000,
            "land": 0,
            "non_flood": 0,
            "scan": 0,
            "smurf": 0,
            "syn_flood": 0,
            "syn_flood_threshold": 10000,
            "tcp_scan": 0,
            "tcp_scan_threshold": 10000,
            "teardrop": 0,
            "udp_flood": 0,
            "udp_flood_threshold": 10000,
            "udp_scan": 0,
            "udp_scan_threshold": 10000,
            "winnuke": 0,
        }
        payload.update(data)
        response = self.session.put(url="v1/protect/", json=payload)
        self.assertEqual(200, response.status_code)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
