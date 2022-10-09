import random
import time
from unittest import TestCase
from utils.core.test_core import ddt, list_data, json_data, yaml_data
from utils.core.session import *
from utils.core.assertion import JsonPathExtractStrategy
import shortuuid
from utils.core.decorators import depends_on
from datetime import date, datetime, timedelta
from settings import supported_protocols
from utils.generator import IPv4Strategy, MACAddressStrategy
import random

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.00000+08:00"


class TestSystemSettings(TestCase):
    session = None
    host = ''
    tags = ['test']
    versions = ['3.4']

    @classmethod
    def setUpClass(cls) -> None:
        user = User(username='test666', password='Bl666666')
        cls.session = AuditorSession()
        cls.session.token_cipher = CipherFactory.create_cipher('auditor/token')
        cls.session.host = cls.host
        cls.session.login(user)
        cls.strategy = JsonPathExtractStrategy()
        cls.cache: dict = {}

    def get_network_state(self):
        response = self.session.request('GET', url=f'/v2/setting/flow-if/')
        return response

    def test_get_network_state(self):
        response = self.session.request('GET', url=f'/v2/setting/ip/')
        self.assertEqual(response.status_code, 200)
        response = self.get_network_state()
        self.assertEqual(response.status_code, 200)

    # @depends_on('test_get_network_state')
    def test_change_monitor_interface(self):
        nic_infos = self.get_network_state().json()
        for _ in range(0, 3):
            nic_choose = random.randint(0, len(nic_infos) - 1)
            nic_infos[nic_choose]['is_flow_interface'] = 'true'
        payload = {
            "if_setting": nic_infos
        }
        response = self.session.request('PUT', url=f'/v2/setting/flow-if/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_syslog_settings(self):
        payload = {
            "ip": "10.30.3.223",
            "port": "514",
            "valid": 'true',
            "protocol": "UDP"
        }
        response = self.session.request('PATCH', url=f'/v2/setting/syslog/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_proto_set(self):
        payload = {
            "ics_protocol_enabled": {
                "ADS/AMS": 'true',
                "BACnet": 'true',
                "CIP": 'true',
                "DNP3": 'true',
                "EGD": 'true',
                "ENIP": 'true',
                "FINS": 'true',
                "Fox": 'true',
                "GE-SRTP": 'true',
                "Hart/IP": 'true',
                "IEC103": 'true',
                "IEC104": 'true',
                "IEC61850/GOOSE": 'true',
                "IEC61850/MMS": 'true',
                "IEC61850/SV": 'true',
                "Modbus": 'true',
                "OpcUA": 'true',
                "Profinet/DCP": 'true',
                "Profinet/RT": 'true',
                "S7COMM": 'true',
                "S7COMM-PLUS": 'true',
                "Umas": 'true',
                "MELSOFT": 'true',
                "EtherCAT": 'true',
                "FF": 'true',
                "H1": 'true',
                "Ovation": 'true',
                "CoAP": 'true',
                "MQTT": 'true',
                "DLT645": 'true'
            },
            "app_protocol_enabled": {
                "FTP": 'true',
                "HTTP": 'true',
                "Telnet": 'true',
                "TFTP": 'true',
                "POP3": 'true',
                "SMTP": 'true'
            },
            "l4_protocol_enabled": {
                "UDP": 'true',
                "TCP": 'true'
            },
            "ip_enabled": None,
            "mac_enabled": None,
            "port_enabled": None
        }
        response = self.session.request('PATCH', url=f'/v2/packet/proto-set/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_snmp(self):
        payload = {
            "active": 'true'
        }
        response = self.session.request('PUT', url=f'/v2/setting/proxy/', json=payload)
        self.assertEqual(response.status_code, 200)
        payload = {
            "versions": [1, 2, 3],
            "trap": "10.30.3.223",
            "group": "public"
        }
        response = self.session.request('PUT', url=f'/v2/setting/config/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_product_info(self):
        response = self.session.request('GET', url=f'/v2/setting/product-info/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    current_time = time.time()
