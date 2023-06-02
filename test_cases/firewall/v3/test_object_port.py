#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 上午11:20
# @Author  : fzf
# @File    : test_object_port.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperatorPwd, FirewallOperator


@ddt
class TestObjectPort(TestCase):
    """
    对象管理-端口对象
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
            {"type": "single",  "remark": "", "members": "12", "portData": 1},
            {"type": "single",  "remark": "", "members": "1-20000", "portData": 1, "reference": 0},
            {"type": "single", "remark": "", "members": "12,12-2000", "portData": 2, "reference": 0}
        ]
    )
    def test_add_address_object(self, data):
        """
        对象管理-端口对象-添加
        """
        payload = {"type": "", "name": shortuuid.ShortUUID().random(length=10), "remark": "", "members": "", "portData": 1}
        payload.update(data)
        response = self.session.post(url="/v1/port/", json=payload).json()
        self.assertEqual(response.get("members"), payload.get("members"))

    def test_delete_address_object(self):
        """
        对象管理-端口对象-删除
        """
        payload = {
            "page": 1,
            "page_size": 20,
        }
        response = self.session.get('/v1/port/', params=payload)
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/port/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
