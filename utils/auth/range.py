import re
from utils.auth.abstract import *
from Crypto.Cipher import AES
import random

from utils.core.decorators import singleton


class Validator:

    @staticmethod
    def validate(_input, regex):
        """
        简单的校验方法，将输入转化为str后使用
        :param _input: 传入的值
        :param regex: 正则规则
        :return: _input是否符合正则
        """
        return True if re.match(regex, _input) else False


class RangesCipher(ICipher):
    def __init__(self):
        super().__init__()
        self.key = 'Bl&2V046640V2&lB'.encode('utf-8')
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, data):
        pass

    def decrypt(self, data):
        pass


@singleton
class RangePasswordCipher(RangesCipher):
    def __init__(self):
        super(RangePasswordCipher, self).__init__()

    def encrypt(self, data):
        """
        加密密码组成为: 8位密码 + 8位盐 + 剩余密码 + 随机填充 + 2位密码长度(十进制字符串)
        加密后总位数是32
        :param data: 原始密码
        :return: 加密后的密码
        """
        password_length = len(data)
        if password_length < 8 or password_length > 16:
            raise ValueError("invalid password!")
        salt = ''.join(random.sample(CHARSET, 8))
        padding_len = 22 - password_length
        padding = ''.join(random.sample(CHARSET, padding_len))
        with_salt = data[:8] + salt + data[8:]
        with_padding = with_salt + padding + '{:02d}'.format(password_length)
        return self.cipher.encrypt(with_padding.encode('latin')).hex().upper()

    def decrypt(self, data):
        """
        解密密码
        :param data: AES加密后的密码
        :return: 解密后的密码
        """
        with_padding = self.cipher.decrypt(bytes.fromhex(data))
        if len(with_padding) != 32:
            raise ValueError("invalid password")
        password_length = int(with_padding[-2:])
        if password_length < 8 or password_length > 16:
            raise ValueError("invalid password")
        password = with_padding[:8] + with_padding[16:8 + password_length]
        # salt = with_padding[8:16]
        return password.decode('latin')


@singleton
class RangeTokenCipher(RangesCipher):
    def __init__(self):
        super(RangeTokenCipher, self).__init__()

    def encrypt(self, data):
        """
        对提供的token进行加密
        :param data: 不加salt的token，长度40或56
        :return: 返回加密并且转换为16进制字符串后的token
        """
        if not Validator.validate(data, r'(^.{40}$)|(^.{56}$)'):
            raise ValueError('invalid token length')
        # 如果是40位的token，则对其增加16位的chaos
        if len(data) == 40:
            data = self.add_chaos(data)
        # 对token加8位的盐
        salt = ''.join(random.sample(CHARSET, 8))
        with_salt = (data[:10] + salt[:2] + data[10:20] + salt[2:4] +
                     data[20:30] + salt[4:6] + data[30:] + salt[6:])
        # 完成加密并转换为十六进制字符串
        return self.cipher.encrypt(with_salt.encode('latin')).hex().upper()

    def decrypt(self, data):
        """
                将已经加密的token进行解密
                :param data: 加密后的token
                :return: 解密后的token list，[包含chaos的token， 不包含chaos的token]
                """
        raw = bytes.fromhex(data)
        if len(raw) != 64:
            raise ValueError('invalid token')
        with_salt = self.cipher.decrypt(raw)
        # 提取带了chaos的token
        token = (with_salt[:10] + with_salt[12:22] + with_salt[24:34] +
                 with_salt[36:62]).decode('latin')
        _ = (with_salt[10:12] + with_salt[22:24] + with_salt[34:36] +
             with_salt[62:])
        # 返回增加获取不包含chaos的token
        return token

    def add_chaos(self, token):
        """
        将token转为每次登录都唯一的token
        :return: 增加每次登录唯一表示的字符串
        """
        chaos = ''.join(random.sample(CHAOS, 16))
        dst_token = token + chaos
        return dst_token

    def get_pure_token(self, token):
        """
        得到唯一的token，需要取出token里的chaos
        :param token: 去除salt后的token
        :return: 真实的用户token，以及是否是重复登录
        """
        src_token, chaos = token[:-16], token[-16:]
        return src_token
