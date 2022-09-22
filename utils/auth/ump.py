from utils.auth.abstract import *
from Crypto.Cipher import AES
import random

from utils.core.decorators import singleton


class UMPCipher(ICipher):
    def __init__(self):
        self.key = b'Bl666666666666lB'
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, data):
        pass

    def decrypt(self, data):
        pass


@singleton
class UMPPasswordCipher(UMPCipher):

    def __init__(self):
        super(UMPPasswordCipher, self).__init__()

    def encrypt(self, data):
        """
       加密密码组成为: 8位密码 + 8位盐 + 剩余密码 + 随机填充 + 2位密码长度(十进制字符串)
       加密后总位数是32
       :param data:
       :return:
       """
        password_length = len(data)
        if password_length < 8 or password_length > 16:
            raise ValueError('Invalid password.')
        salt = ''.join(random.sample(CHARSET, 8))
        # 总长32，盐8，密码长2，密码和填充22
        padding_len = 22 - password_length
        padding = ''.join(random.sample(CHARSET, padding_len))
        with_salt = data[:8] + salt + data[8:]
        with_padding = with_salt + padding + '{:02d}'.format(password_length)
        return self.cipher.encrypt(with_padding.encode('latin')).hex()

    def decrypt(self, data):
        with_padding = self.cipher.decrypt(bytes.fromhex(data))
        if len(with_padding) != 32:
            raise ValueError('Invalid password!')
        password_length = int(with_padding[-2:])
        if password_length < 8 or password_length > 16:
            raise ValueError('Invalid password!')
        password = with_padding[:8] + with_padding[16:8 + password_length]
        return password.decode('latin')


@singleton
class UMPTokenCipher(UMPCipher):
    def __init__(self):
        super(UMPTokenCipher, self).__init__()

    def encrypt(self, data):
        if len(data) != 40:
            raise ValueError('Token must be 40 chars!')
        salt = ''.join(random.sample(CHARSET, 8))
        with_salt = data[:10] + salt[:2] + data[10:20] + salt[2:4] + data[20:30] + salt[4:6] + data[30:] + salt[6:]

        return self.cipher.encrypt(with_salt.encode('latin')).hex()

    def decrypt(self, data):
        raw = bytes.fromhex(data)
        if len(raw) != 48:
            raise ValueError('Invalid token!')
        with_salt = self.cipher.decrypt(raw)
        token = (with_salt[:10] + with_salt[12:22] + with_salt[24:34] + with_salt[36:46]).decode('latin')
        # salt = with_salt[10:12] + with_salt[22:24] + with_salt[34:36] + with_salt[46:]
        return token
