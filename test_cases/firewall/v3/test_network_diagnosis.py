#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:33
# @Author  : fzf
# @File    : test_network_diagnosis.py
# @Software: PyCharm
import time
import unittest
from unittest import TestCase

from utils.setting import *
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestNetworkDiagnosis(TestCase):
    """
    网络管理：网络诊断
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


    def _get_ping_status(self, _id):
        response = self.session.get(url=f"/v1/network/diagnosis/ping/{_id}/").json()
        return response.get("state")

    def test_diagnosis_ping(self):
        """
        网络管理：网络诊断-ping
        """
        timeout = 40
        payload = {
            "count": "4",
            "deadline": "10",
            "host": TestIP,
            "interface": None,
            "interval": "1",
            "packetsize": "64",
            "timeout": "5",
        }
        response = self.session.post(url="/v1/network/diagnosis/ping", json=payload)
        self.assertEqual(201, response.status_code)
        #  判断Ping状态
        #  结束或者超时，退出任务
        while self._get_ping_status(response.json().get("id")) == "PENDING" and timeout > 0:
            time.sleep(1)
            timeout -= 1

    def _get_tracert_status(self, _id):
        response = self.session.get(url=f"/v1/network/diagnosis/traceroute/{_id}/").json()
        return response.get("state")

    def test_diagnosis_tracert(self):
        timeout = 40
        """
        网络管理：网络诊断-tracert
        """
        payload = {
            "host": TestIP,
            "interface": None,
            "ttl": "20",
            "wailtime": "5",
        }
        response = self.session.post(url="/v1/network/diagnosis/traceroute", json=payload)
        self.assertEqual(201, response.status_code)
        #  判断Ping状态
        #  结束或者超时，退出任务
        while self._get_tracert_status(response.json().get("id")) == "PENDING" and timeout > 0:
            time.sleep(1)
            timeout -= 1

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
