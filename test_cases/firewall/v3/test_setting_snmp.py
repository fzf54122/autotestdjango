#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/1 上午9:30
# @Author  : fzf
# @File    : test_setting_snmp.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *
from utils.setting import FirewallOperator, FirewallOperatorPwd


def SNMPClient(host: str):
    v1result = os.popen('snmpwalk -v 1 -c public ' + host + ' ' + "1.3.6.1.2.1.1.1").read().split('\n')[:-1]
    v2result = os.popen('snmpwalk -v 2c -c public ' + host + ' ' + "1.3.6.1.2.1.1.1").read().split('\n')[:-1]
    v3result = os.popen(
        'snmpwalk -v 3 -u bolean -a SHA -A admin123 -x AES -X admin123 -l authPriv  ' + host + ' ' + "1.3.6.1.2.1.1.1").read().split(
        '\n')[:-1]
    return [v1result[0], v2result[0], v3result[0]]


class TestSettingSnmp(TestCase):
    """
    SNMP：V1、V2、V3测试
    无SNMP_TRAP测试
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

    def SNMP(self, status: bool):
        """
        开启SNMP服务
        """
        payload = {"active": status}
        response = self.session.patch(url="/v1/setting/snmp/proxy/", json=payload).json()
        self.assertEqual(response.get("active"), True)
        self.SNMPCreate()

    def SNMPCreate(self):
        """
        添加SNMPV3用户
        """
        payload = {
            "auth_password": "admin123",
            "auth_type": 3,
            "encryption_password": "admin123",
            "encryption_type": 3,
            "username": "fzf001"
        }
        response = self.session.post(url="/v1/setting/snmp/user/", json=payload).json()
        self.assertEqual(response.get("username"), payload.get("username"))

    def test_snmp_service(self):
        """
        系统设置：SNMP-V1、V2、V3测试
        """
        self.SNMP(True)
        response = SNMPClient(self.host)
        self.assertEqual(response[0], response[1])
        self.assertEqual(response[1], response[2])

    def test_snmp_user_remove(self):
        """
        系统设置：SNMP-删除全部用户
        """
        response = self.session.delete(url="v1/setting/snmp/user")
        self.assertEqual(response.status_code, 204)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()


if __name__ == '__main__':
    unittest.main()
