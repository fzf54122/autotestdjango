#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 下午4:09
# @Author  : fzf
# @File    : test_policy_custom.py
# @Software: PyCharm
import json
import random
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import Policy_DIP, Policy_SIP,FirewallOperator,FirewallOperatorPwd


@ddt
class TestPolicyCustom(TestCase):
    """
    自定义协议
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
            {"action": "pass","features": [{"match_type": 1, "byte_offset": "1", "byte_width": "2", "byte_feature": "qw", "feature_type": "string"}]},
            {"action": "alert","features":[{"match_type": 1, "byte_offset": "2", "byte_width": "2", "byte_feature": "00", "feature_type": "hex"}]},
            {"action": "alert", "protocol": "TCP","features":[{"match_type": 1, "byte_offset": "3", "byte_width": "2", "byte_feature": "qw", "feature_type": "string"}]},
            {"action": "alert", "protocol": "UDP","features": [{"match_type": 1, "byte_offset": "4", "byte_width": "2", "byte_feature": "00", "feature_type": "hex"}]},
            {"action": "alert", "protocol": "UDP","features": [{"match_type": 1, "byte_offset": "5", "byte_width": "2", "byte_feature": "qw", "feature_type": "string"}]},
            {"action": "alert", "protocol": "UDP","features": [{"match_type": 2, "data_offset": "17", "data_length": "2", "data_match_char": ">", "data_order": "大端","data_feature": "12"}], },
        ]
    )
    def test_custom_policy_add(self, data):
        """
        安全策略：自定义协议-添加
        """
        payload = {
            "action": "drop",
            "active": True,
            "dst_ip": Policy_DIP,
            "dst_port": random.randint(200, 2000),
            "features": [{"match_": 1, "byte_of": "1", "byte_w": "2", "byte_fea": "qw", "feature_": "string"}],
            "name": shortuuid.ShortUUID().random(length=10),
            "protocol": "TCP",
            "src_ip": Policy_SIP,
            "src_port": random.randint(100, 1000),
            "time_object": None,
        }
        payload.update(data)
        response = self.session.post(url="v1/policy/custom/", json=payload)
        self.assertEqual(response.status_code, 201)

    def test_custom_policy_del(self):
        """
        安全策略：自定义协议-删除
        """
        payload = {
            "page": 1,
            "page_size": 50,
        }
        response = self.session.get(url="v1/policy/custom/", params=payload).json()
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/policy/custom/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
