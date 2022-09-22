from .firewall import *
from .range import *
from .ump import *
from .auditor import *


class CipherFactory:
    """Cipher工厂"""
    cipher_map = {}

    @classmethod
    def create_cipher(cls, key) -> ICipher:
        if key in cls.cipher_map:
            return cls.cipher_map[key]
        else:
            cls._init_cipher(key)
            return cls.cipher_map[key]

    @classmethod
    def _init_cipher(cls, key):
        if key.lower() == 'range/token':
            cls.cipher_map[key] = RangeTokenCipher()
        elif key.lower() == 'range/password':
            cls.cipher_map[key] = RangePasswordCipher()
        elif key.lower() == 'ump/token':
            cls.cipher_map[key] = UMPTokenCipher()
        elif key.lower() == 'ump/password':
            cls.cipher_map[key] = UMPPasswordCipher()
        elif key.lower() == 'firewall/token':
            cls.cipher_map[key] = FirewallTokenCipher()
        elif key.lower() == 'firewall/password':
            cls.cipher_map[key] = FirewallPasswordCipher()
        elif key.lower() == 'auditor/password':
            cls.cipher_map[key] = AuditorPasswordCipher()
        elif key.lower() == 'auditor/token':
            cls.cipher_map[key] = AuditorTokenCipher()
        else:
            raise AttributeError("Invalid key, not supported yet")
