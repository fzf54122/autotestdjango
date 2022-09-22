import random
import time
from unittest import TestCase
from unittestreport import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.core.assertion import JsonPathExtractStrategy
from settings import host
import shortuuid
from utils.core.decorators import depends_on
from datetime import date, datetime, timedelta
from settings import supported_protocols
from utils.generator import IPv4Strategy, MACAddressStrategy
import random

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestSystemSettings(TestCase):
    session = None

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache: dict = {}


if __name__ == '__main__':
    current_time = time.time()
