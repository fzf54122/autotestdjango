#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:31
# @Author  : fzf
# @File    : test_network_vpn.py
# @Software: PyCharm
import time
import unittest
from unittest import TestCase

import shortuuid

from utils.setting import FirewallOperatorPwd,FirewallOperator
from utils.core.test_core import ddt, list_data
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestNetworkVPN(TestCase):
    """
    网络管理：VPN
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

    @list_data([
        {},
        {"security_proto": "AH"},
        {"auth_type": 1, "encap_mode": "tunnel", "ike_version": 2,  "l2tp_local_ip": "",
         "remote_ip": "192.168.3.122", "subnets": [{"srubnet": "192.168.1.0/24", "drubnet": "192.168.10.0/24"}]},
        {"auth_type": 1, "encap_mode": "tunnel", "ike_version": 2,  "l2tp_local_ip": "",
         "remote_ip": "192.168.3.122", "subnets": [{"srubnet": "192.168.1.0/24", "drubnet": "192.168.10.0/24"}],
         "security_proto": "AH"},
    ])
    def test_network_vpn_add(self, data):
        """
        网络管理：VPN-添加
        """
        payload = {
            "active": True,
            "auth_type": 2,
            "compress": False,
            "dpdaction": "none",
            "dpddelay": 30,
            "dpdtimeout": 150,
            "encap_mode": "transport",
            "exchange_mode": 1,
            "exchange_status": False,
            "ike_algorithm": [],
            "ike_version": 1,
            "ikelifetime": 28800,
            "ipsec_algorithm": [],
            "is_keyingtries_forever": False,
            "keyingtries": 3,
            "l2tp_ip_range": ["192.168.1.0", "192.168.1.255"],
            "l2tp_local_ip": "192.168.1.254",
            "local_iface": "lan1",
            "local_ip": "192.168.3.145",
            "name": shortuuid.ShortUUID().random(length=20),
            "nat_t": False,
            "password": "admin123",
            "pfs": True,
            "psk": "admin123",
            "remote_ip": "",
            "salifetime": 10800,
            "security_proto": "ESP",
            "subnets": [],
            "username": "admin",
        }
        payload.update(data)
        response = self.session.post(url="v1/network/ipsecvpn/", json=payload)
        time.sleep(3)
        self.assertEqual(201, response.status_code)

    def test_network_vpn_del(self):
        """
        网络管理：VPN-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/network/ipsecvpn/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/network/ipsecvpn/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
