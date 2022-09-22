# 数据类（构造常用数据类型、UUID、文本、词组、文件链接、文件路径）
# 安全类（构造操作系统信息、HASH加密、密码）
# 信息类（构造个人信息数据和表单信息数据：姓名、地址、电话、工作、证件号、
# 银行卡号、公司、邮箱、生日)
# 网络类（构造IP MAC HTTP的客户端类型和文件类型，反反爬）
import random
import re

from faker import Factory
from utils.file_reader import JsonReader
from jsf import JSF
from abc import ABC, abstractmethod
import sys
import inspect


# 等价于设置语言区
fake = Factory.create('zh_CN')


class IStrategy(ABC):

    @abstractmethod
    def handle(self):
        pass


class StringStrategy(IStrategy):

    def handle(self, min_chars: int = None, max_chars: int = None, string_format: str = None):
        """
        string_format 优先级高于min_chars 与 max_chars
        :param string_format:
        :param max_chars:
        :param min_chars:
        :return:
        """
        return fake.pystr(min_chars, max_chars) if not string_format else fake.pystr_format(string_format)


class TextStrategy(IStrategy):
    def handle(self, max_nb_chars: int = None):
        return fake.text(max_nb_chars)


class IPv4Strategy(IStrategy):

    def handle(self, area: str = None, network: bool = False, address_class: str = None, **kwargs):
        if not area:
            return fake.ipv4(network, address_class)
        elif area == 'private':
            return fake.ipv4_private(network, address_class)
        elif area == 'public':
            return fake.ipv4_public(network, address_class)
        else:
            return fake.ipv4(network, address_class)


class BooleanStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.pybool()


class UUIDStrategy(IStrategy):
    def handle(self, **kwargs):
        pass


class AddressStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.address()


class NameStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.name()


class HostNameStrategy(IStrategy):
    def handle(self, levels: int = 1, **kwargs):
        return fake.hostname(levels)


class ImageUrlStrategy(IStrategy):
    def handle(self, width: int = None, height: int = None, **kwargs):
        return fake.image_url(width, height)


class MACAddressStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.mac_address()


class PortStrategy(IStrategy):
    def handle(self, is_system: bool = False, is_user: bool = False, is_dynamic: bool = False, **kwargs):
        """
        端口号策略
        :param is_dynamic: 动态端口/私有端口/临时端口，49152-65535
        :param is_user: 用户常用端口或注册的端口，1024-49151
        :param is_system: 是否使用系统或常见服务端口，0-1023
        :param kwargs:
            is_system: 是否使用系统或常见服务端口，0-1023
            is_user: 用户常用端口或注册的端口，1024-49151
            is_dynamic: 动态端口/私有端口/临时端口，49152-65535
            端口定义可见： https://datatracker.ietf.org/doc/html/rfc6335
        :return:
        """
        return fake.port_number(is_system, is_user, is_dynamic)


class FileStrategy(IStrategy):
    def handle(self, depth: int = 1, absolute: bool = True, **kwargs):
        return fake.file_path(depth=depth, absolute=absolute)


class PhoneNumberStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.phone_number()


class OSInfoStrategy(IStrategy):
    def handle(self, os_type: str = 'win', **kwargs):
        if os_type == 'win':
            return fake.windows_platform_token() + ' ' + fake.linux_processor()
        if os_type == 'linux':
            return fake.linux_processor()
        if os_type == 'mac':
            return fake.mac_platform_token()
        if os_type == 'ios':
            return fake.ios_platform_token()
        if os_type == 'android':
            return fake.android_platform_token()
        return None


class BrowserStrategy(IStrategy):
    def handle(self, browser_type: str = 'chrome', **kwargs):
        if browser_type == 'chrome':
            return fake.chrome()
        elif browser_type == 'firefox':
            return fake.firefox()
        elif browser_type == 'ie':
            return fake.internet_explorer()
        elif browser_type == 'safari':
            return fake.safari()
        elif browser_type == 'opera':
            return fake.opera()
        else:
            return fake.user_agent()


class ProfileStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.profile()


class SSNStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.ssn()


class BirthStrategy(IStrategy):
    def handle(self, minimum_age: int = None, maximum_age: int = None, **kwargs):
        return fake.date_of_birth(minimum_age=minimum_age, maximum_age=maximum_age)


class EmailStrategy(IStrategy):
    def handle(self, domain: str = '123.com', **kwargs):
        return fake.email(domain=domain)


class JobStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.job()


class PasswordStrategy(IStrategy):
    def handle(self, length=10, special_chars=False, digits=True, upper_case=False, lower_case=False, **kwargs):
        return fake.password(length=length,
                             special_chars=special_chars,
                             digits=digits,
                             upper_case=upper_case,
                             lower_case=lower_case)


class CreditCard(IStrategy):
    def handle(self, **kwargs):
        return fake.credit_card_full(), fake.credit_card_number()


class HashStrategy(IStrategy):
    def handle(self, raw_output: bool = False, **kwargs):
        return {'md5': fake.md5(raw_output), 'sha1': fake.sha1(raw_output), 'sha256': fake.sha256(raw_output)}


class CompanyStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.company()


class IPv6Strategy(IStrategy):
    def handle(self, **kwargs):
        return fake.ipv6()


class MimeTypeStrategy(IStrategy):
    def handle(self, mime_type: str = 'application', **kwargs):
        return fake.mime_type(mime_type)


class WordStrategy(IStrategy):
    def handle(self, **kwargs):
        return fake.word(), fake.words()


class IntegerStrategy(IStrategy):
    def handle(self, min_value: int = 1, max_value: int = 65534, **kwargs):
        return fake.pyint(min_value, max_value)


def get_classes():
    """获取module下所有的class"""
    return list(filter(lambda x: x[0].endswith('Strategy') and x[0] != 'IStrategy', inspect.getmembers(sys.modules[__name__], inspect.isclass)))


def convert_big_camp(bc_string: str):
    pattern = r"(?:[A-Z][a-z]+)|OS|MAC|UUID|IPv4|IPv6|SSN"
    return "_".join(re.findall(pattern, bc_string)).lower()


class FakeStrategyFactory:
    FakeStrategyMap: dict = {}
    class_members = get_classes()
    for class_member in class_members:
        class_name = convert_big_camp(class_member[0])
        FakeStrategyMap[class_name] = class_member[1]()

    @classmethod
    def get_strategy(cls, strategy_type):
        return cls.FakeStrategyMap[strategy_type]


class FakeStrategyContext:

    def __init__(self, strategy):
        self.__strategy = strategy

    @property
    def strategy(self):
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy):
        self.__strategy = strategy

    def get_random_data(self, **kwargs):
        self.__strategy.handle(**kwargs)


class DataGenerator:

    @classmethod
    def generate_from_schema_by_jsf(cls, schema: dict = None):
        if not schema:
            return None
        else:
            faker = JSF(schema)
            return faker.generate()

    @classmethod
    def generate_from_schema(cls, schema: dict = None):
        data: dict = {}
        if not schema:
            return None
        else:
            required_filed = schema.get('required', [])
            # 生成必填项的数据
            for filed in required_filed:
                filed_type = schema['properties'][filed]['type']
                strategy_type = f'{filed_type}_strategy'
                strategy = FakeStrategyFactory.get_strategy(strategy_type)
                data[filed] = strategy.handle()
            # 生成非必填数据
            option_filed = list(filter(lambda x: x not in required_filed, schema['properties'].keys()))
            sample_filed = random.sample(option_filed, k=random.randint(1, len(option_filed)))
            for filed in sample_filed:
                filed_type = schema['properties'][filed]['type']
                strategy_type = f'{filed_type}_strategy'
                strategy = FakeStrategyFactory.get_strategy(strategy_type)
                data[filed] = strategy.handle()
        return data


if __name__ == '__main__':
    schema = JsonReader('/Users/heweidong/PycharmProjects/AutoTest/src/swagger/demo.json').data
    print(DataGenerator.generate_from_schema(schema))
    # print(DataGenerator.generate_from_schema_by_jsf(random_text))
    ...

    # print(re.findall(pattern, 'TestHelpOSInfoHelpStrategy'))
