#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 下午4:58
# @Author  : fzf
# @File    : test_object_address.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperatorPwd, FirewallOperator


@ddt
class TestObjectAddress(TestCase):
    """
    对象管理-地址对象
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
            {"type": "IP", "members": "1.1.1.1", "remark": "", "addressData": 1},
            {"type": "range", "members": "2.2.2.2/2,1.1.1.1-2.2.2.2", "remark": "", "addressData": 2},
            {"type": "IP_CIDR", "members": "3.3.3.3/2", "remark": "", "addressData": 1}
        ]
    )
    def test_add_address_object(self, data):
        """
        对象管理-地址对象-添加
        """
        payload = {
            "type": "IP", "name": shortuuid.ShortUUID().random(length=10), "members": "1.1.1.1", "remark": "",
            "addressData": 1
        }
        payload.update(data)
        response = self.session.post(url="/v1/address/", json=payload).json()
        self.assertEqual(response.get("members"), payload.get("members"))

    def test_delete_address_object(self):
        """
        对象管理-地址对象-删除
        """
        payload = {
            "page": 1,
            "page_size": 20,
        }
        response = self.session.get('/v1/address/', params=payload)
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/address/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
