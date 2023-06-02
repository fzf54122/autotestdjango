#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:31
# @Author  : fzf
# @File    : test_network_nat.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.setting import *
from utils.core.test_core import ddt, list_data
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestNetworkNAT(TestCase):
    """
    网络管理：NAT
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

    def test_network_nat_snat_add(self):
        """
        网络管理：NAT:SNAT-添加
        """
        payload = {"name": shortuuid.ShortUUID().random(length=10), "src": PolicyConnectSIP, "dst": PolicyConnectDIP,
                   "active": True}
        response = self.session.post(url="/v1/policy/nat/snat/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_network_nat_snat_update(self):
        """
        网络管理：NAT:SNAT-编辑
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/nat/snat/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            payload = {"name": shortuuid.ShortUUID().random(length=10), "src": PolicyConnectSIP, "dst": PolicyConnectDIP,
                       "active": False}
            response = self.session.patch(url="/v1/policy/nat/snat/{}'.format(_id)", json=payload)
            self.assertEqual(200, response.status_code)

    def test_network_nat_snat_del(self):
        """
        网络管理：NAT:SNAT-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/nat/snat/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/nat/snat/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {"active": True},
        {"active": False,"sport": "10023"},
        {"active": False,"sport": "10024"},
        {"protocol": "UDP","sport": "10025"},
    ])
    def test_network_nat_dnat_add(self,data):
        """
        网络管理：NAT:DNAT-添加
        """
        payload = {"active": True,
                   "dport": "10022",
                   "dst": PolicyConnectDIP,
                   "name": shortuuid.ShortUUID().random(length=10),
                   "protocol": "TCP",
                   "sport": "10022",
                   "src": PolicyConnectSIP, }
        payload.update(data)
        response = self.session.post(url="/v1/policy/nat/dnat/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_network_nat_dnat_update(self):
        """
        网络管理：NAT:DNAT-编辑
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/nat/dnat/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            payload = {"active": False,
                       "dport": "10022",
                       "dst": PolicyConnectDIP,
                       "name": shortuuid.ShortUUID().random(length=10),
                       "protocol": "TCP",
                       "sport": "10022",
                       "src": PolicyConnectSIP, }
            response = self.session.patch(url="/v1/policy/nat/dnat/1/", json=payload)
            self.assertEqual(200, response.status_code)

    def test_network_nat_dnat_del(self):
        """
        网络管理：NAT:DNAT-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/policy/nat/dnat/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/nat/dnat/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
