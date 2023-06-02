#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:31
# @Author  : fzf
# @File    : test_network_routing.py
# @Software: PyCharm
import unittest
import shortuuid
from unittest import TestCase

from utils.setting import *
from utils.core.test_core import list_data, ddt
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestNetworkRouting(TestCase):
    """
    网络管理：路由设置
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
        {"des": "1.1.1.1/24", "dev": None, "type": "via", "via": "10.10.10.10", },
        {"des": "2.2.2.2/24", "dev": "lan1", "type": "dev", "via": None, },
    ])
    def test_network_route_add(self, data):
        """
        网络管理：路由设置: 静态路由-添加
        """
        payload = {
            "des": "1.1.1.1/24",
            "dev": None,
            "type": "via",
            "via": "10.10.10.10",
        }
        payload.update(data)
        response = self.session.post(url="/v1/network/route/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_network_route_del(self):
        """
        网络管理：路由设置: 静态路由-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/network/route/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/network/route/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {"active": True, },
        {"active": False, "dst_ip": "2.2.2.3", },
        {"active": True, "dst_ip": "2.2.2.2", },
        {"active": True, "dst_ip": "2.2.2.2/24", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "", "interface": "lan1",
         "next_hop": "", "priority": 100, "protocol_type": "ICMP", "src_ip": "2.2.2.2/24", "src_port": "", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "10022", "interface": "lan1",
         "next_hop": "", "priority": 100, "protocol_type": "UDP", "src_ip": "2.2.2.2/24", "src_port": "10022", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "10022", "interface": "lan1",
         "next_hop": "", "priority": 100, "protocol_type": "TCP", "src_ip": "2.2.2.2/24", "src_port": "10022", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "", "interface": "lan1",
         "next_hop": "", "priority": 100, "protocol_type": "ALL", "src_ip": "2.2.2.2/24", "src_port": "", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "", "interface": "",
         "next_hop": "192.168.1.100", "priority": 100, "protocol_type": "ICMP", "src_ip": "2.2.2.2/24",
         "src_port": "", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "10022", "interface": "",
         "next_hop": "192.168.1.100", "priority": 100, "protocol_type": "UDP", "src_ip": "2.2.2.2/24",
         "src_port": "10022", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "10022", "interface": "",
         "next_hop": "192.168.1.100", "priority": 100, "protocol_type": "TCP", "src_ip": "2.2.2.2/24",
         "src_port": "10022", },
        {"active": True, "dst_ip": "1.1.1.1/24", "dst_port": "", "interface": "",
         "next_hop": "192.168.1.100", "priority": 100, "protocol_type": "ALL", "src_ip": "2.2.2.2/24", "src_port": "", }
    ])
    def test_network_policy_route_add(self, data):
        """
        网络管理：路由设置: 策略路由-添加
        """
        payload = {
            "active": True,
            "dst_ip": "",
            "dst_port": "",
            "interface": "lan1",
            "name": shortuuid.ShortUUID().random(length=20),
            "next_hop": "",
            "priority": 100,
            "protocol_type": "ALL",
            "src_ip": "1.1.1.1/24",
            "src_port": "",
        }
        payload.update(data)
        response = self.session.post(url="/v1/network/policy-route/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_network_policy_route_del(self):
        """
        网络管理：路由设置: 策略路由-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/network/policy-route/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/network/policy-route/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @list_data([
        {"active": True, },
        {"active": False, }
    ])
    def test_network_rip_base(self, data):
        """
        网络管理：路由设置: RIP-配置
        """
        payload = {"active": True, }
        payload.update(data)
        response = self.session.patch(url="/v1/network/rip/base/", json=payload)
        self.assertEqual(200, response.status_code)

    @list_data([
        {"auth_type": "no auth", "interface": "lan1", "key": None, "key_id": None, "password": None,
         "receive_version": "RIP1", "send_version": "RIP1", "split_horizon": 1, },
        {"auth_type": "no auth", "interface": "lan1", "key": None, "key_id": None, "password": None,
         "receive_version": "RIP1", "send_version": "RIP2", "split_horizon": 1, },
        {"auth_type": "no auth", "interface": "lan1", "key": None, "key_id": None, "password": None,
         "receive_version": "RIP1", "send_version": "RIP1 and RIP2", "split_horizon": 1, },
        {"auth_type": "no auth", "interface": "lan1", "key": None, "key_id": None, "password": None,
         "receive_version": "RIP2", "send_version": "RIP2", "split_horizon": 1, },
        {"auth_type": "no auth", "interface": "lan1", "key": None, "key_id": None, "password": None,
         "receive_version": "RIP2", "send_version": "RIP1 and RIP2", "split_horizon": 1, },
    ])
    def test_network_rip_add(self, data):
        """
        网络管理：路由设置: RIP-添加
        """
        payload = {
            "auth_type": "no auth",
            "interface": "lan1",
            "key": None,
            "key_id": None,
            "password": None,
            "receive_version": "RIP1 and RIP2",
            "send_version": "RIP2",
            "split_horizon": 1,
        }
        payload.update(data)
        response = self.session.post(url="/v1/network/rip/", json=payload)
        self.assertEqual(201, response.status_code)

    def test_network_rip_del(self):
        """
        网络管理：路由设置: RIP-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/network/rip/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/network/rip/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
