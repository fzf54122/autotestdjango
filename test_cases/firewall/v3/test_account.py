#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 上午11:21
# @Author  : fzf
# @File    : test_account.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.setting import *
from utils.auth import CipherFactory
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.decorators import depends_on
from utils.core.session import *


class TestAccount(TestCase):
    """
    group：
    Operator：操作员
    Auditor：审计员
    auth_type: 
    0: 不认证
    1：radius认证
    2：APP口令认证
    """
    password_cipher = CipherFactory.create_cipher('firewall/password')
    session = None
    tags = ['test']
    versions = ['3.2']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='admin', password='Admin@123')
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_create_operator(self) -> None:
        """
        创建操作员
        """
        data = {
            'username': FirewallOperator,
            'password1': self.password_cipher.encrypt(FirewallOperatorPwd),
            'password2': self.password_cipher.encrypt(FirewallOperatorPwd),
            'group': 'Operator',
            'description': '',
            'auth_type': 0,
            'is_active': 'true'
        }
        self.CheckResponse(data=data)

    @depends_on('test_create_operator')
    def test_create_auditor(self):
        """
        创建审计员
        """
        data = {
            'username': FirewallAuditor,
            'password1': self.password_cipher.encrypt(FirewallAuditorPwd),
            'password2': self.password_cipher.encrypt(FirewallAuditorPwd),
            'group': 'Auditor',
            'description': '',
            'auth_type': 0,
            'is_active': 'true'
        }
        self.CheckResponse(data=data)

    @depends_on('test_create_operator')
    def test_create_radius(self):
        """
        创建radius认证用户
        """
        data = {
            'username': 'fzf200',
            'password1': self.password_cipher.encrypt('admin123'),
            'password2': self.password_cipher.encrypt('admin123'),
            'group': 'Auditor',
            'description': '',
            'auth_type': 1,
            'is_active': 'true'
        }
        self.CheckResponse(data=data)

    @depends_on('test_create_operator')
    def test_create_google_password(self):
        """
        创建口令认证用户
        """
        data = {
            'username': 'fzfgoogle100',
            'password1': self.password_cipher.encrypt('admin123'),
            'password2': self.password_cipher.encrypt('admin123'),
            'group': 'Auditor',
            'description': '',
            'auth_type': 2,
            'is_active': 'true'
        }
        self.CheckResponse(data=data)

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()

    def CheckResponse(self, data):
        response = self.session.request('POST', url=f'/v1/user/', json=data)
        message = self.strategy.extract(response, '$.id')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '1005')


if __name__ == '__main__':
    unittest.main()
