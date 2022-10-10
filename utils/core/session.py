import logging
from typing import Dict
from urllib.parse import urljoin

from requests import Session, Response
import requests
from abc import ABC, abstractmethod
from utils.log import get_logger
from utils.exceptions import StatusCodeException
from utils.log import logged
from utils.auth import CipherFactory, ICipher
from pydantic import BaseModel
from AutoTestDjango.settings.base import API_TIME_OUT


class User(BaseModel):
    username: str
    password: str


# 关闭证书警告
requests.packages.urllib3.disable_warnings()

logger = get_logger(__file__)


class ISession(Session, ABC):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        super(ISession, self).__init__(*args, **kwargs)

    @abstractmethod
    def authorize(self):
        """负责处理每个请求的鉴权问题, 子类必须实现这个方法实现"""
        pass

    def _check_response(self, response: Response):
        """检查响应状态等内容"""
        # check_status:
        error_code = (502, 500, 503, 400, 403, 401, 404,)
        if response.status_code in error_code:
            logger.error(f'error_code detected {response.text}')
            raise StatusCodeException(response.status_code)
        # TODO: check response content

    def _enclose_url(self, url: str) -> str:
        """确保url收否以/结尾，如果请求是post等方法时，需要保证url enclosed"""
        if not url.endswith('/'):
            return url + '/'
        else:
            return url

    def _fill_url(self, url: str, scheme: str = 'https'):
        """拼凑完整url"""
        enclosed_url = self._enclose_url(url)
        return urljoin(f'{scheme}://{self.host}', enclosed_url)

    def _convert_json(self, obj: Dict):
        """递归转换json中的布尔值True为字符串类型的true，主要是接口调用时需要转换"""
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (list, tuple)):
            return [self._convert_json(item) for item in obj]
        if isinstance(obj, dict):
            return {self._convert_json(key): self._convert_json(value) for key, value in obj.items()}
        return obj

    def request(self, method: str = "GET", url: str = '', *args, **kwargs) -> Response:
        """发起请求"""
        supported_methods = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')
        if method.upper() not in supported_methods:
            raise ValueError(f'method not supported, supported: {supported_methods}, given: {method}')
        url = self._fill_url(url)
        # 未登录且没有标记不需要登录时，直接抛出认证异常
        self.authorize()

        # 正式发送请求
        response = super().request(method=method.upper(), url=url, *args, **kwargs, timeout=API_TIME_OUT)
        # self._check_response(response)
        return response

    def get(self, url=None, *args, **kwargs):
        return self.request(method='GET', url=url, *args, **kwargs)

    def post(self, url=None, *args, **kwargs):
        return self.request(method='POST', url=url, *args, **kwargs)

    def put(self, url=None, *args, **kwargs):
        return self.request(method='PUT', url=url, *args, **kwargs)

    def delete(self, url=None, *args, **kwargs):
        return self.request(method='DELETE', url=url, *args, **kwargs)

    def patch(self, url=None, *args, **kwargs):
        return self.request(method='PATCH', url=url, *args, **kwargs)


class BoleanSession(ISession):
    """
    Web session， 使用header中的字段进行鉴权，authorize主要对header进行操作
    """
    def __init__(self):
        self._host: str = ''
        super().__init__(self._host)
        self.verify = False
        self.token = None
        self._token_cipher = None
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
        })

    @property
    def token_cipher(self):
        return self._token_cipher

    @token_cipher.setter
    def token_cipher(self, cipher: ICipher):
        self._token_cipher = cipher

    @logged(level=logging.INFO)
    def authorize(self):
        """处理token加密，如果token为None则不产生任何影响"""
        # 已经登录存在token；视为已经登录，那么每次请求前需要更新header中的token
        if self.token is not None:
            headers = {
                'Authorization': 'Token {}'.format(self.token_cipher.encrypt(self.token))
            }
            self.headers.update(headers)
        # token为None，则处于未登录状态，不做处理

    @abstractmethod
    def login(self, user):
        pass

    @abstractmethod
    def logout(self):
        pass


class AuditorSession(BoleanSession):

    """审计的session"""
    def login(self, user: User):
        password_cipher = CipherFactory.create_cipher('auditor/password')
        data = {
            'password': password_cipher.encrypt(user.password),
            'username': user.username
        }
        response = self.request("POST", url="/v2/user/login/", json=data).json()
        encrypted_token = response.get("token")
        self.token = self.token_cipher.decrypt(encrypted_token)
        return response

    def logout(self):
        """登出平台，会重置token和header"""
        self.request(url="/v2/user/logout/")
        self.token = None
        if 'Authorization' in self.headers.keys():
            self.headers.pop('Authorization')


class FirewallSession(BoleanSession):

    def login(self, user: User):
        password_cipher = CipherFactory.create_cipher('firewall/password')
        data = {
            'password': password_cipher.encrypt(user.password),
            'username': user.username
        }
        response = self.request("POST", url="/v1/user/login/", json=data).json()
        encrypted_token = response.get("token")
        self.token = self.token_cipher.decrypt(encrypted_token)
        return response

    def logout(self):
        self.request(url="/v1/user/logout/")
        self.token = None
        if 'Authorization' in self.headers.keys():
            self.headers.pop('Authorization')


class SessionFactory:
    """session工厂"""
    @staticmethod
    def create_session(session_type: str) -> BoleanSession:
        if session_type == 'auditor':
            return AuditorSession()
        elif session_type == 'firewall':
            return FirewallSession()
        else:
            raise ValueError('session type not supported')

# class RangeSession(BoleanSession):
#     """靶场session"""
#
#     def login(self, user):
#         """靶场登录，会自动设定session中的token"""
#         # 申请验证码
#         self.request('POST', url=urljoin(f"https://{HOST}", "/api/v1/user/captcha/"), json={"captcha": user.captcha})
#         password_cipher = PasswordCipher()
#         # 登录
#         data = {
#             "username": user.username,
#             "password": password_cipher.encrypt(user.password),
#             "captcha": user.captcha
#         }
#         response = self.request("POST", url=urljoin(f"https://{HOST}", "/api/v1/user/login/"), json=data).json()
#         encrypted_token = response.get("token")
#         self.token, _ = self.token_cipher.decrypt(encrypted_token)
#         return response
#
#     def logout(self):
#         """登出平台，会重置token和header"""
#         self.request(url=urljoin(f"https://{HOST}", "/api/v1/user/logout/"))
#         self.token = None
#         if 'Authorization' in self.headers.keys():
#             self.headers.pop('Authorization')


if __name__ == "__main__":
    # session = RangeSession()
    # session.login(user=User(username='rangetools', password='Admin@123', telephone='18309208729', real_name='hello',
    #                         captcha='2222', email='rangetools@163.com'))
    # resp = session.request("GET", url=urljoin(f"https://{HOST}", "/api/v1/home/profile/"))
    # session.logout()
    # print(resp)
    ...
