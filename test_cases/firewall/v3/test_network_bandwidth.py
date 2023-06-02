#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午5:31
# @Author  : fzf
# @File    : test_network_bandwidth.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.setting import *
from utils.core.test_core import ddt, list_data
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


@ddt
class TestNetworkBandWidth(TestCase):
    """
    网络管理：带宽管理
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
        {"active": False, "top_speed":99},
        {"active": True, "top_speed":100}
    ])
    def test_network_bandwidth_add(self, data):
        """
        网络管理：带宽管理-添加
        """
        payload = {
            "active": False,
            "bottom_speed": 100,
            "income_interface": "lan2",
            "name": shortuuid.ShortUUID().random(length=10),
            "out_interface": "lan1",
            "policies":
                [{"band_width": None,
                  "dst_ip": "",
                  "dst_port": None,
                  "id": 1,
                  "protocol": None,
                  "src_ip": "",
                  "src_port": None,
                  "time_object": None}],
            "priority": None,
            "top_speed": 100,
        }
        payload.update(data)
        response = self.session.post(url="/v1/network/bandwidth/", json=payload)
        self.assertEqual(201, response.status_code)
        self.assertEqual(payload.get("active"), response.json().get("active"))

    def test_network_bandwidth_del(self):
        """
        网络管理：带宽管理-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="/v1/network/bandwidth/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/network/bandwidth/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
