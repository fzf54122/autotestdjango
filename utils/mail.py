# 发件人
# 收件人1， 收件人2.。。
# 发件人登录邮箱
# 编写主题
# 编写正文
# 添加附件
# 发送邮件

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
import re
from smtplib import SMTP


class Email:

    def __init__(self,
                 sender: str,
                 receiver: [str, list],
                 title: str,
                 server: str,
                 auth_code: str,
                 message: str = None,
                 attachment_file: [str, list] = None
                 ):
        self.sender = sender
        self.receiver = receiver
        self.title = title
        self.message = message
        self.attachment_file = attachment_file
        self.server = server
        self.auth_code = auth_code

        self.msg = MIMEMultipart('related')

    def send(self):
        self.msg['Subject'] = self.title
        self.msg['From'] = self.sender
        self.msg['To'] = self.receiver

        if self.message:
            self.msg.attach(MIMEText(self.message))

        if self.attachment_file:
            if isinstance(self.attachment_file, str):
                self._attach_file(self.attachment_file)
            if isinstance(self.attachment_file, list):
                for _path in self.attachment_file:
                    self._attach_file(_path)

        smtp_server = SMTP(self.server)
        smtp_server.login(self.sender, self.auth_code)
        smtp_server.sendmail(self.sender, self.receiver, self.msg.as_string())
        smtp_server.quit()

    def _attach_file(self, file_path):
        if not exists(file_path):
            raise FileNotFoundError(f'{file_path}:附件文件不存在或者附件文件路径错误！')
        with open(file_path, 'r', encoding='utf-8') as f:
            att = MIMEText(f.read(), 'plain', 'utf-8')
        att['Content-Type'] = 'application/octet-stream'
        file_name = re.split(r'[\\|/]', file_path)[-1]
        att['Content-Disposition'] = f'attachment; filename="{file_name}"'
        self.msg.attach(att)


# email = Email(sender='xxxx@qq.com',
#               receiver='xxx@qq.com',
#               title='title',
#               server='smtp.qq.com',
#               auth_code='xxxxxxxxx',
#               message='xxxx',
#               attachment_file=r'D:\Program Files\JetBrains\imooc\report.html'
# )
