#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 下午1:58
# @Author  : fzf
# @File    : test_auser_login.py
# @Software: PyCharm
import unittest
from unittest import TestCase

from utils.setting import *
from utils.core.assertion import JsonPathExtractStrategy
from utils.core.session import *


class TestLogin(TestCase):
    """
    操作员、审计员、radius、google口令：用户登陆
    """
    password_cipher = CipherFactory.create_cipher('firewall/password')
    session = None
    tags = ['test']
    versions = ['3.2']
    host = ''

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username="admin", password="Admin@123")
        cls.session = FirewallSession()
        cls.session.token_cipher = CipherFactory.create_cipher('firewall/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()

    def test_login_operator(self) -> None:
        """
        操作员登录
        """
        self.login(user=FirewallOperator, password=FirewallOperatorPwd)

    def test_login_auditor(self) -> None:
        """
        审计员登录
        """
        self.login(user=FirewallAuditor, password=FirewallAuditorPwd)

    def test_login_radius(self) -> None:
        """
        Radius用户登录
        """
        if self.bind_radius():
            self.login(user='fzf200', password='admin123')
            self.remove_radius()

    def test_login_google_password(self) -> None:
        """
        口令认证用户登录
        """
        self.login(user='fzfgoogle100', password='admin123')

    @classmethod
    def tearDownClass(cls):
        cls.session.logout()
        cls.session.close()

    def bind_radius(self):
        payload = {
            "auth_type": 2,
            "expiration_time": 5,
            "ip": "10.30.6.188",
            "port": 1812,
            "repeat_auth": 3,
            "shared_secret": "admin123",
        }
        response = self.session.patch(url='v1/user/radius/', json=payload).json()
        self.assertEqual(response.get("ip"), payload.get("ip"))
        return True

    def remove_radius(self):
        payload = {
            "active": False,
        }
        response = self.session.patch(url='v1/user/radius/', json=payload).json()
        self.assertEqual(response.get("active"), False)

    def login(self, user: str, password: str) -> None:
        user = User(username=user, password=password)
        data = {
            'password': self.password_cipher.encrypt(user.password),
            'username': user.username
        }
        response = self.session.request("POST", url="/v1/user/login/", json=data).json()
        self.assertEqual(response.get('username'), user.username)


if __name__ == '__main__':
    unittest.main()
