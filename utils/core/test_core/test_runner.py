import json
import os
import unittest
import time
from concurrent.futures.thread import ThreadPoolExecutor
from utils.core.test_core.test_result import TestResult, ReRunResult
from utils.core.test_core.result_push import DingTalk, WeiXin, SendEmail
from jinja2 import Environment, FileSystemLoader
import copy
import logging

Load = unittest.defaultTestLoader
logger = logging.getLogger(__file__)


class TestRunner:

    def __init__(self, suite: unittest.TestSuite,
                 filename="report.html",
                 report_dir="./reports",
                 title='测试报告',
                 tester='测试员',
                 desc="XX项目测试生成的报告",
                 host='',
                 templates=1,
                 console=False
                 ):
        """
        :param suite [object]: 测试套件，由多个case组成，unittest的TestSuite对象, required
        :param filename [string]: 报告文件的名称, defaults = report.html
        :param report_dir [string]: 生成的报告地址, defaults = ./reports
        :param title [string]: 套件名称(报告中使用的标题), defaults = 测试报告
        :param templates [integer]: 报告模板,  defaults = 1
        :param tester [string]: 负责人， defaults = 测试员
        """
        if not isinstance(suite, unittest.TestSuite):
            raise TypeError("Parameter suite is not a test suite")
        if not isinstance(filename, str):
            raise TypeError("filename is not str")
        if not filename.endswith(".html"):
            filename = filename + ".html"
        self.suite = suite
        self.filename = filename
        self.title = title
        self.tester = tester
        self.desc = desc
        self.templates = templates
        self.report_dir = report_dir
        self.result = []
        self.start_time = time.time()
        self.host = host
        self.console = console

    def __classification_suite(self):
        suites_list = []

        def wrapper(suite):
            for item in suite:
                # 如果suite中的item包含testcase类
                if isinstance(item, unittest.TestCase):
                    suites_list.append(suite)
                    # 追加类变量
                    current_class = item.__class__
                    setattr(current_class, 'host', self.host)
                    break
                else:
                    wrapper(item)
        wrapper(copy.deepcopy(self.suite))
        return suites_list

    def __get_reports(self):
        if self.console:
            print("所有用例执行完毕，正在生成测试报告中......")
        logger.info("所有用例执行完毕，正在生成测试报告中......")
        test_result = {
            "success": 0,
            "all": 0,
            "fail": 0,
            "skip": 0,
            "error": 0,
            "results": [],
            "testClass": [],
        }
        for res in self.result:
            for item in test_result:
                test_result[item] += res.fields[item]

        test_result['runtime'] = '{:.2f} S'.format(time.time() - self.start_time)
        test_result["begin_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))
        test_result["title"] = self.title
        test_result["tester"] = self.tester
        test_result['desc'] = self.desc
        if test_result['all'] != 0:
            test_result['pass_rate'] = '{:.2f}'.format(test_result['success'] / test_result['all'] * 100)
        else:
            test_result['pass_rate'] = 0
        # 判断是否要生产测试报告
        if os.path.isdir(self.report_dir):
            pass
        else:
            os.mkdir(self.report_dir)
        # 获取历史执行数据
        test_result['history'] = self.__handle_history_data(test_result)

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(template_path))
        if self.templates == 2:
            template = env.get_template('templates2.html')
        elif self.templates == 3:
            template = env.get_template('templates3.html')
        else:
            template = env.get_template('templates.html')
        file_path = os.path.join(self.report_dir, self.filename)
        res = template.render(test_result)
        with open(file_path, 'wb') as f:
            f.write(res.encode('utf8'))
        if self.console:
            print("测试报告已经生成，报告路径为:{}".format(file_path))
        logger.info("测试报告已经生成，报告路径为:{}".format(file_path))
        self.email_conent = {"file": os.path.abspath(file_path),
                             "content": env.get_template('templates03.html').render(test_result)
                             }
        self.test_result = test_result
        return test_result

    def __handle_history_data(self, test_result):
        """
        处理历史数据
        :return:
        """
        try:
            with open(os.path.join(self.report_dir, 'history.json'), 'r', encoding='utf-8') as f:
                history = json.load(f)
        except FileNotFoundError as e:
            history = []
        history.append({'success': test_result['success'],
                        'all': test_result['all'],
                        'fail': test_result['fail'],
                        'skip': test_result['skip'],
                        'error': test_result['error'],
                        'runtime': test_result['runtime'],
                        'begin_time': test_result['begin_time'],
                        'pass_rate': test_result['pass_rate'],
                        })

        with open(os.path.join(self.report_dir, 'history.json'), 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=True)
        return history

    def __get_notice_content(self):
        """获取通知的内容"""
        template_path = os.path.join(os.path.dirname(__file__), '../templates')
        env = Environment(loader=FileSystemLoader(template_path))
        res_text = env.get_template('dingtalk.md').render(self.test_result)
        return res_text

    def run(self, thread_count=1, count=0, interval=2):
        """
        The entrance to running tests
        Note: if multiple test classes share a global variable, errors may occur due to resource competition
        :param thread_count:Number of threads. default 1
        :param count: Rerun times,  default 0
        :param interval: Rerun interval, default 2
        :return: Test run results
        """
        suites = self.__classification_suite()
        with ThreadPoolExecutor(max_workers=thread_count) as ts:
            for i in suites:
                # res = TestResult()
                res = ReRunResult(count=count, interval=interval)
                self.result.append(res)
                ts.submit(i.run, result=res).add_done_callback(res.stopTestRun)
            ts.shutdown(wait=True)
        result = self.__get_reports()
        return result

    def rerun_run(self, count=0, interval=2):
        """
        失败/异常用例重运行
        :param count: 重运行次数,  defaults to 0
        :param interval: 重运行间隔, defaults to 2
        :return: 执行结果对象
        """
        res = ReRunResult(count=count, interval=interval)
        self.result.append(res)
        suites = self.__classification_suite()
        for case_ in suites:
            print(type(case_))
            case_.run(res)
        res.stopTestRun()
        res = self.__get_reports()
        return res

    def send_email(self, host: str, port: int, user: str, password: str, to_addrs, is_file=True):
        """
        将运行结果发送邮件，运行中的用例会自动绑定到邮件
        :param host: SMTP 服务器地址
        :param port: SMTP 服务器端口
        :param user: Email 地址
        :param password: SMTP 服务端需要的token
        :param to_addrs: 邮件发送目标，可以是单独或列表
        :param is_file: 是否是文件对象
        :return:
        """
        sm = SendEmail(host=host, port=port, user=user, password=password)
        if is_file:
            filename = self.email_conent["file"]
        else:
            filename = None
        content = self.email_conent["content"]

        sm.send_email(subject=self.title, content=content, filename=filename, to_addrs=to_addrs)

    def get_except_info(self):
        """获取报错用例或失败用例的错误信息"""
        except_info = []
        num = 0
        for i in self.result:
            for texts in i.failures:
                t, content = texts
                num += 1
                except_info.append("*{}、用例【{}】执行失败*，\n失败信息如下：".format(num, t._testMethodDoc))
                except_info.append(content)
            for texts in i.errors:
                num += 1
                t, content = texts
                except_info.append("*{}、用例【{}】执行错误*，\n错误信息如下：".format(num, t._testMethodDoc))
                except_info.append(content)
        except_str = "\n".join(except_info)
        return except_str

    def dingtalk_notice(self, url, key=None, secret=None, at_mobiles=None, is_all=False, except_info=False):
        """
        :param url: 钉钉机器人的Webhook地址
        :param key: （非必传：str类型）如果钉钉机器人安全设置了关键字，则需要传入对应的关键字
        :param secret:（非必传:str类型）如果钉钉机器人安全设置了签名，则需要传入对应的密钥
        :param at_mobiles: （非必传，list类型）发送通知钉钉中要@人的手机号列表，如：[137xxx,188xxx]
        :param is_all: 是否@所有人，默认为False,设为True则会@所有人
        :param except_info:是否发送未通过用例的详细信息，默认为False，设为True则会发送失败用例的详细信息
        :return:  发送成功返回 {"errcode":0,"errmsg":"ok"}  发送失败返回 {"errcode":错误码,"errmsg":"失败原因"}
        """

        res_text = self.__get_notice_content()
        if except_info:
            res_text += '\n ### 未通过用例详情：\n'
            res_text += self.get_except_info()
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": '{}({})'.format(self.title, key),
                "text": res_text
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": is_all
            }
        }
        ding = DingTalk(url=url, data=data, secret=secret)
        response = ding.send_info()
        return response.json()

    def weixin_notice(self, chat_id, access_token=None, corp_id=None, corp_secret=None):
        """
        测试结果推送到企业微信群，【access_token】和【corp_id，corp_secret】至少要传一种
        可以传入access_token ,也可以传入（corp_id，corp_secret）来代替access_token
        :param chat_id: 企业微信群ID
        :param access_token: 调用企业微信API接口的凭证
        :param corp_id: 企业ID
        :param corp_secret:应用的凭证密钥
        :return:
        """
        # 获取通知结果
        res_text = self.__get_notice_content()
        data = {
            "chatid": chat_id,
            "msgtype": "markdown",
            "markdown": {
                "content": res_text
            }
        }
        wx = WeiXin(access_token=access_token, corp_id=corp_id, corp_secret=corp_secret)
        response = wx.send_info(data=data)
        return response
