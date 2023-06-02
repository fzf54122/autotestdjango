#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 下午4:18
# @Author  : fzf
# @File    : test_policy_base.py
# @Software: PyCharm
import json
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperatorPwd, FirewallOperator


@ddt
class TestPolicyBase(TestCase):
    """
    安全策略
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
            {"mode": "test", "default_drop": True},
            {"mode": "test", "default_drop": True, "dpi": True, "flow_detect": True, "black_detect": True},
            {"mode": "work", "default_drop": False, "dpi": False, "flow_detect": False, "black_detect": False},
            {"mode": "work", "default_drop": True, "dpi": True, "flow_detect": True, "black_detect": True},
            {"mode": "study", "default_drop": False, "dpi": False, "flow_detect": False, "black_detect": False},
            {"mode": "study", "default_drop": True, "dpi": True, "flow_detect": True, "black_detect": True},
        ]
    )
    def test_firewall_mode(self, data):
        """
        安全策略：防火墙模式
        """
        payload = {"mode": "test", "default_drop": False, "dpi": False, "flow_detect": False, "black_detect": False}
        payload.update(data)
        response = self.session.put(url="v1/policy/", json=payload)
        try:
            self.assertEqual(response.status_code, 200)
        except AssertionError as e:
            error = self.strategy.extract(response, '$.error')
            if len(error) == 1:
                self.assertEqual(error[0], '1111')
            else:
                raise e

    @list_data(
        [
            {'action': 'pass'},
            {'action': 'alert'},
            {'action': 'drop'},
            {'protocol': 'ICMP'},
            {'protocol': 'TCP', "state": ["New", "Established", "Invalid", "Related"]},
            {'protocol': 'HTTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 80},
            {'protocol': 'FTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 21},
            {'protocol': 'POP3', "state": ["New", "Established", "Invalid", "Related"], 'dport': 110},
            {'protocol': 'Telnet', "state": ["New", "Established", "Invalid", "Related"], 'dport': 23},
            {'protocol': 'SMTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 25},
            {'protocol': 'DNS(TCP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 53},
            {'protocol': 'DNS(UDP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 53},
            {'protocol': 'TFTP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 69},
            {'protocol': 'HTTPS', "state": ["New", "Established", "Invalid", "Related"], 'dport': 443},
            {'protocol': 'SNMP', "state": ["New", "Established", "Invalid", "Related"], 'dport': 161},
            {'protocol': 'SNMP(trap)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 161},
            {'protocol': 'H323(RAS)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 1719},
            {'protocol': 'H323(Q931)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 1720},
            {'protocol': 'RTSP(UDP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 554},
            {'protocol': 'RTSP(TCP)', "state": ["New", "Established", "Invalid", "Related"], 'dport': 554},
        ]
    )
    def test_base_firewall_add(self, data):
        """
        安全策略：基础防火墙-添加
        """
        payload = {
            "action": "pass",
            "active": True,
            "dip": "",
            "dipType": 0,
            "dipobj": None,
            "dipobj_name": None,
            "dport": None,
            "dportType": 0,
            "dportobj": None,
            "dportobj_name": None,
            "name": shortuuid.ShortUUID().random(length=20),
            "protocol": "DNS(TCP)",
            "protocolType": 0,
            "protocolobj": None,
            "protocolobj_name": None,
            "sip": "",
            "sipType": 0,
            "sipobj": None,
            "sipobj_name": None,
            "smac": None,
            "sport": None,
            "sportType": 0,
            "sportobj": None,
            "sportobj_name": None,
            "state": None,
            "time_object": None,
        }
        payload.update(data)
        response = self.session.post(url="v1/policy/basic/", data=json.dumps(payload))
        self.assertEqual(201, response.status_code)

    def test_base_firewall_del(self):
        """
        安全策略：基础防火墙-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/basic/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/basic/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
