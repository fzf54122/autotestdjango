#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 上午11:20
# @Author  : fzf
# @File    : test_object_proto.py
# @Software: PyCharm
import unittest
from unittest import TestCase

import shortuuid

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.core.test_core import ddt, list_data
from utils.setting import FirewallOperatorPwd, FirewallOperator


@ddt
class TestObjectProto(TestCase):
    """
    对象管理-协议对象
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
            {"reference": 0,  "remark": "", "members": "POP3"},
            {"reference": 0, "remark": "","members": "POP3,DNS(TCP),DNS(UDP),FTP,SMTP,Telnet,SNMP(trap),RTSP(UDP),RTSP(TCP),HTTPS,HTTP,TFTP,SNMP"},
        ]
    )
    def test_add_address_object(self, data):
        """
        对象管理-协议对象-添加
        """
        payload = {"reference": 0, "name": shortuuid.ShortUUID().random(length=10), "remark": "", "members": "POP3"}
        payload.update(data)
        response = self.session.post(url="/v1/protocol/", json=payload).json()
        self.assertEqual(response.get("members"), payload.get("members"))

    def test_delete_address_object(self):
        """
        对象管理-协议对象-删除
        """
        payload = {
            "page": 1,
            "page_size": 20,
        }
        response = self.session.get('/v1/protocol/', params=payload)
        ids = self.strategy.extract(response, '$.results[*].id')
        for _id in ids:
            response = self.session.delete('/v1/protocol/{}'.format(_id))
            self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
