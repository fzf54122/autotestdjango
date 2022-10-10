from utils.auth import CipherFactory
from utils.core.session import SessionFactory, User
from test_cases.auditor.settings import ADMIN_USER, TEST_USER


class Preparation:
    session = SessionFactory.create_session('auditor')
    session.token_cipher = CipherFactory.create_cipher('auditor/token')

    @classmethod
    def prepare_user(cls):
        cls.session.login(User(username=ADMIN_USER[0], password=ADMIN_USER[1]))
        password_cipher = CipherFactory.create_cipher('auditor/password')
        for username, password, group in TEST_USER:
            data = {
                'username': username,
                'password1': password_cipher.encrypt(password),
                'password2': password_cipher.encrypt(password),
                'groups': group,
                'description': None
            }
            cls.session.post(url='/v2/user/', json=data)
