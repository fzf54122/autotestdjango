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

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestWhiteList(TestCase):
    session = None

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.rule_name = shortuuid.ShortUUID().random(length=20)

    def list_whitelist(self):
        data = {
            'page': 1,
            'is_learned': None,
            'search': None,
            'protocol': None,
            'ordering': None,
            'is_active': None,
            'page_size': 20
        }
        response = self.session.request('GET', url=f'https://{host}/v2/white-list/', params=data)
        return response

    def test_get_list(self):
        response = self.list_whitelist()
        self.assertEqual(response.status_code, 200)

    def test_create_white_list(self):

        data = {
            "name": self.rule_name,
            "is_active": 'true',
            "src_ip": None,
            "dst_ip": None,
            "src_mac": None,
            "dst_mac": None,
            "src_ports": None,
            "dst_ports": None,
            "protocol": "S7COMM",
            "industry_content": "special",
            "rule": [
                {
                    "rosctr": 1,
                    "function_code": 4,
                    "subfunction": None,
                    "area": 7,
                    "address": [
                        "1"
                    ],
                    "value":[
                        "123"
                    ]
                }
            ]
        }

        response = self.session.request('POST', url=f'https://{host}/v2/white-list/', json=data)
        message = self.strategy.extract(response, '$.name')
        if len(message) == 0:
            message = self.strategy.extract(response, '$.error')
            self.assertGreater(len(message), 0)
            self.assertEqual(message[0], '已存在相同的白名单策略名称')

    @depends_on('test_create_white_list')
    def test_delete_white_list(self):
        search_data = {
            'page': 1,
            'is_learned': None,
            'search': self.rule_name,
            'protocol': None,
            'ordering': None,
            'is_active': None,
            'page_size': 100
        }
        response = self.session.request('GET', url=f'https://{host}/v2/white-list/', params=search_data)
        rule_id = self.strategy.extract(response, '$.results.[0].id')[0]
        response = self.session.request('DELETE', url=f'https://{host}/v2/white-list/{rule_id}/')
        self.assertEqual(response.status_code, 204)

    def check_learning_status(self):
        response = self.session.request('GET',  url=f'https://{host}/v2/white-list/learned/is_learning/')
        status = self.strategy.extract(response, '$.status')
        if len(status) == 0:
            raise ValueError('响应内容异常，未提取到status字段')
        return status[0]

    def test_white_list_learning(self):
        start_params = {
            "start_time": datetime.now().strftime(TIME_FORMAT),
            "end_time": (datetime.now() + timedelta(minutes=5)).strftime(TIME_FORMAT),
            "ip_range": None,
            "include_ipv6": 'false',
            "protocols": [
                "ADS/AMS",
                "BACnet",
                "CIP",
                "DNP3",
                "EGD",
                "ENIP",
                "FINS",
                "Fox",
                "GE-SRTP",
                "Hart/IP",
                "IEC103",
                "IEC104",
                "IEC61850/GOOSE",
                "IEC61850/MMS",
                "IEC61850/SV",
                "Modbus",
                "OpcUA",
                "Profinet/DCP",
                "Profinet/RT",
                "S7COMM",
                "S7COMM-PLUS",
                "Umas",
                "MELSOFT",
                "EtherCAT",
                "FF",
                "H1",
                "Ovation",
                "CoAP",
                "MQTT",
                "DLT645",
                "FTP",
                "HTTP",
                "Telnet",
                "TFTP",
                "POP3",
                "SMTP",
                "TCP",
                "UDP"
            ]
        }
        response = self.session.request('POST', url=f'https://{host}/v2/white-list/study/start/', json=start_params)
        self.assertEqual(response.status_code, 200)

        while self.check_learning_status() != 0:
            time.sleep(1)
        else:
            response = self.session.request('POST', url=f'https://{host}/v2/white-list/learned/')
            self.assertEqual(response.status_code, 200)
            response = self.list_whitelist()
            learned_protocol = self.strategy.extract(response, '$.results.[*].protocol')
            for protocol in learned_protocol:
                self.assertIn(protocol, supported_protocols)

    def test_enable_all(self):
        enable_params = {
            'is_active': 'true'
        }
        response = self.session.request('PUT', url=f'https://{host}/v2/white-list/', json=enable_params)
        self.assertEqual(response.status_code, 200)

    @depends_on('test_enable_all')
    def test_disable_all(self):
        disable_params = {
            'is_active': 'false'
        }
        response = self.session.request('PUT', url=f'https://{host}/v2/white-list/', json=disable_params)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    ...
