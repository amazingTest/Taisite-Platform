from utils import common
from models.caseSuite import CaseSuite
from models.testingCase import TestingCase
from models.mailSender import MailSender
from testframe.interfaceTest.tester import tester
from models.testReport import TestReport
from models.project import Project
import pymongo
from bson import ObjectId
import datetime
import requests
import time
import copy


class Cron:

    stop_alert_and_wait_until_resume = {}
    recorded_first_failed_time = {}
    recorded_first_failed_report_id = {}

    def __init__(self, cron_name, test_case_suite_id_list, test_domain,  trigger_type, is_execute_forbiddened_case=False,
                 test_case_id_list=None, alarm_mail_list=None, is_ding_ding_notify=False, ding_ding_access_token=None,
                 ding_ding_notify_strategy=None, is_enterprise_wechat_notify=False, enterprise_wechat_access_token=None,
                 enterprise_wechat_notify_strategy=None, is_web_hook=False, retry_limit=3, retry_interval=60, global_vars=None,
                 **trigger_args):

        if test_case_id_list is None:
            test_case_id_list = []

        if isinstance(test_case_suite_id_list, list) and isinstance(test_case_id_list, list):
            self.test_case_suite_id_list = list(set(test_case_suite_id_list))
            self.test_case_id_list = list(set(test_case_id_list))
        else:
            raise TypeError('test_case_suite_id_list and test_case_id_list must be list！')

        if isinstance(test_domain, str):
            self.test_domain = test_domain
        else:
            raise TypeError('test_domain must be string！')

        if isinstance(trigger_type, str) and trigger_type in ["interval", "date", "cron"]:
            self.trigger_type = trigger_type
        else:
            raise TypeError('trigger_type is invalid!')

        self.trigger_args = trigger_args
        self.is_execute_forbiddened_case = is_execute_forbiddened_case
        self.status_history = {}

        self.ding_ding_access_token = ding_ding_access_token if is_ding_ding_notify else None
        self.ding_ding_notify_strategy = {'success': True, 'fail': True}\
            if is_ding_ding_notify and ding_ding_notify_strategy is None else ding_ding_notify_strategy

        self.enterprise_wechat_access_token = enterprise_wechat_access_token if enterprise_wechat_access_token else None
        self.enterprise_wechat_notify_strategy = {'success': True, 'fail': True} \
            if is_enterprise_wechat_notify and enterprise_wechat_notify_strategy is None\
                else enterprise_wechat_notify_strategy

        self._id = str(common.get_object_id())
        self.alarm_mail_list = []

        if alarm_mail_list:
            if isinstance(alarm_mail_list, list):
                for alarm_mail in alarm_mail_list:
                    if isinstance(alarm_mail, str) and common.is_valid_email(alarm_mail):
                        self.alarm_mail_list.append(alarm_mail)
                    else:
                        raise TypeError('<%s> is invalid mail!' % alarm_mail)
            else:
                raise TypeError('mail_list must be list')

        self.is_web_hook = is_web_hook

        self.report_id = None  # 告警时发送测试报告生成_id
        self.report_created_time = None  # 告警时发送测试报告生成时间
        self.failed_count = 0  # 用于判断是否邮件发送告警

        self.cron_name = cron_name
        self.current_retry_count = 0  # 记录当前定时任务尝试次数
        self.retry_limit = retry_limit  # 定时任务报错后重试次数限制
        self.retry_interval = retry_interval  # 定时任务报错后重试时间间隔

        self.global_vars = global_vars if global_vars else {}

    def get_cron_test_cases_list(self):
        if not self.is_execute_forbiddened_case:
            for case_suite_id in self.test_case_suite_id_list:
                is_forbiddened_case_suite = len(list(CaseSuite.find({'_id': ObjectId(case_suite_id),
                                                                     'status': {'$ne': True}}))) > 0
                if is_forbiddened_case_suite:
                    self.test_case_suite_id_list.remove(case_suite_id)

        query = {'isDeleted': {'$ne': True}} if self.is_execute_forbiddened_case\
            else {'isDeleted': {'$ne': True}, 'status': True}
        test_cases = [testing_case for testing_case in TestingCase.find(query).sort([('caseSuiteId', pymongo.ASCENDING),
                                                                                     ('createAt', pymongo.ASCENDING)])]

        cron_test_cases_from_case_suite_id = filter(lambda x: str(x.get('caseSuiteId')) in self.test_case_suite_id_list,
                                                    test_cases)
        cron_test_cases_from_case_id = filter(lambda x: str(x.get('_id')) in self.test_case_id_list, test_cases)

        cron_test_cases_list = list(cron_test_cases_from_case_suite_id) + list(cron_test_cases_from_case_id)

        def remove_duplicated_case(case_list):
            id_list = []
            for case in case_list:
                case_id = case["_id"]
                if case_id in id_list:
                    case_list.remove(case)
                else:
                    id_list.append(case_id)
            return case_list

        return remove_duplicated_case(cron_test_cases_list)

    def get_id(self):
        return self._id

    def generate_test_report(self, project_id, cron_id, test_result_list, total_test_spending_time, project_name):

        test_count = len(test_result_list)
        passed_count = len(
            list(filter(lambda x: x == 'ok', [test_result["status"] for test_result in test_result_list])))
        # failed count 已在生成报告前进行计算
        # failed_count = len(
        #     list(filter(lambda x: x == 'failed', [test_result["status"] for test_result in test_result_list])))
        passed_rate = '%d' % round((passed_count / test_count) * 100, 2) + '%'

        self.report_created_time = datetime.datetime.now()
        failed_count = self.failed_count

        execute_from = "WebHook" if hasattr(self, 'is_web_hook') and self.is_web_hook else f"定时任务 - {self.cron_name}"

        raw_data = {
            "projectId": ObjectId(project_id),
            "projectName": project_name,
            "testCount": test_count,
            "passCount": passed_count,
            "failedCount": failed_count,
            "passRate": passed_rate,
            "comeFrom": execute_from,
            "executorNickName": "定时机器人",
            "cronId": cron_id,
            "totalTestSpendingTimeInSec": total_test_spending_time,
            "testDomain": self.test_domain,
            "testDetail": test_result_list,
            "createAt": datetime.datetime.utcnow()  # 存入库时什么datetime都当utc使
        }
        filtered_data = TestReport.filter_field(raw_data, use_set_default=True)
        report_id = TestReport.insert(
            filtered_data
        )
        self.report_id = report_id

    def send_ding_ding_notify(self, title, content, headers=None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        hook_url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(self.ding_ding_access_token)
        data = {"msgtype": "markdown", "markdown": {"title": title, "text": content}}
        res = requests.post(url=hook_url, json=data, headers=headers)
        return res

    def send_enterprise_wechat_notify(self, title, content, headers=None, send_report_file=True):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        hook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(self.enterprise_wechat_access_token)
        data = {"msgtype": "markdown", "markdown": {"content": "{} \n >{}".format(title, content)}}
        text_notify_res = requests.post(url=hook_url, json=data, headers=headers)
        if send_report_file:
            file_notify_res = self.send_enterprise_wechat_file(
                file_content=TestReport.get_test_report_excel_bytes_io(self.report_id).read())
            if not file_notify_res.status_code == 200:
                raise BaseException('企业微信发送异常: {}'.format(file_notify_res.text))
        return text_notify_res

    def send_enterprise_wechat_file(self, file_content, file_name='test-report.xlsx'):

        post_file_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?" \
                        f"key={self.enterprise_wechat_access_token}&type=file"

        files = {'file': (file_name, file_content, 'application/octet-stream')}
        post_file_res = requests.post(url=post_file_url, files=files,
                                      headers={'Content-Type': 'multipart/form-data'}).json()

        media_id = post_file_res.get('media_id', '')

        json_data = {
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        }

        hook_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.enterprise_wechat_access_token}'
        hook_res = requests.post(url=hook_url, json=json_data, headers={'Content-Type': 'application/json'})
        return hook_res  # {'errcode': 0, 'errmsg': 'ok'}

    def send_report_to_staff(self, project_id, mail_list, mail_title, mail_content,
                             attachment_name, attachment_content):
        if not isinstance(mail_list, list):
            raise TypeError("mail_list must be list!")
        # if self.failed_count < 1:
        #     raise TypeError('测试全通过，不需要发送告警报告！')
        if not self.report_created_time:
            raise TypeError('无测试报告生成时间，报告发送失败！')

        json_data = dict()
        json_data['mail_list'] = mail_list
        json_data['mail_title'] = mail_title
        json_data['mail_content'] = mail_content
        json_data['attachment_name'] = attachment_name
        json_data['attachment_content'] = attachment_content
        result = common.send_email(MailSender, project_id, json_data)

        return result

    def cron_mission(self):
        # print(self.stop_alert_and_wait_until_resume )
        cron_test_cases_list = self.get_cron_test_cases_list()
        if len(cron_test_cases_list) > 0:
            project_id = cron_test_cases_list[0]["projectId"]
            project_name = Project.find_one({'_id': ObjectId(project_id)})['name']
        else:
            raise TypeError('定时任务执行中未找到任何可执行用例！')

        _global_vars = self.global_vars if hasattr(self, 'global_vars') else {}

        tester_for_cron = tester(test_case_list=cron_test_cases_list,
                                 domain=self.test_domain,
                                 global_vars=_global_vars)

        total_test_start_time = time.time()

        test_result_list = tester_for_cron.execute_all_test_for_cron_and_single_test()

        total_test_end_time = time.time()

        total_test_spending_time = round(total_test_end_time - total_test_start_time, 3)

        for index, test_result in enumerate(test_result_list):
            test_result = common.format_response_in_dic(test_result)
            test_result_list[index] = test_result

        if not len(test_result_list):
            return

        self.failed_count = len(
            list(filter(lambda x: x == 'failed', [test_result["status"] for test_result in test_result_list])))

        self.current_retry_count += 1 if self.failed_count > 0 else -self.current_retry_count

        generate_retry_cron = self.failed_count > 0 and self.current_retry_count < self.retry_limit

        self.generate_test_report(project_id, self.get_id(), test_result_list, total_test_spending_time, project_name)

        if generate_retry_cron:

            print(f'当前失败用例个数:{self.failed_count}')
            print(f'正在重试第 {self.current_retry_count} 次')

            time.sleep(self.retry_interval)

            self.cron_mission()

        else:
            is_send_mail = self.failed_count > 0 and isinstance(self.alarm_mail_list, list) \
                           and len(self.alarm_mail_list) > 0

            is_send_ding_ding = self.ding_ding_access_token if hasattr(self, 'ding_ding_access_token') else False

            is_send_enterprise_wechat = self.enterprise_wechat_access_token if hasattr(self,
                                                                                       'enterprise_wechat_access_token') \
                else False

            finally_passed_and_send_resume_notify = not self.failed_count and self.stop_alert_and_wait_until_resume.get(self.cron_name)

            failed_again_but_wait_for_resume = self.failed_count and self.stop_alert_and_wait_until_resume.get(self.cron_name)

            if finally_passed_and_send_resume_notify:

                print(f'finally_passed_and_send_resume_notify... report id: {self.report_id}')

                if is_send_enterprise_wechat:

                    enterprise_wechat_title = '### 接口测试平台企业微信服务'
                    enterprise_wechat_content = f' ✅️ {project_name} 项目 \n\n > 👍️️️️ {self.cron_name} 测试通过 \n\n ' \
                                                f'> 😄 于 {self.recorded_first_failed_time[self.cron_name]} 发生的告警已恢复～ \n\n ' \
                                                f'> 过往报错报告id: {self.recorded_first_failed_report_id[self.cron_name]} \n\n' \
                                                f'> 最新生成报告id: {self.report_id} \n\n > ⬇️ 此时下方应有最新报告详情 '

                    if hasattr(self, 'enterprise_wechat_notify_strategy'):
                        enterprise_wechat_res = self.send_enterprise_wechat_notify(title=enterprise_wechat_title,
                                                                                   content=enterprise_wechat_content)
                        if not enterprise_wechat_res.status_code == 200:
                            raise BaseException('企业微信发送异常: {}'.format(enterprise_wechat_res.text))

                if is_send_ding_ding:
                    dingding_title = '### 接口测试平台钉钉服务'
                    dingding_content = f' ✅️ {project_name} 项目 \n\n > 👍️️️️ {self.cron_name} 测试通过 \n\n ' \
                                       f'> 😄 于 {self.recorded_first_failed_time[self.cron_name]} 发生的告警已恢复～ \n\n ' \
                                       f'> 过往报错报告id: {self.recorded_first_failed_report_id[self.cron_name]} \n\n' \
                                       f'> 最新生成报告id: {self.report_id}'

                    if hasattr(self, 'ding_ding_notify_strategy'):
                        dingding_res = self.send_ding_ding_notify(title=dingding_title, content=dingding_content)
                        if not dingding_res.status_code == 200:
                            raise BaseException('钉钉发送异常: {}'.format(dingding_res.text))

                mesg_title = '接口测试平台告警恢复提醒 ：）'
                mesg_content = "Dears: \n\n 于 【{}】 【{}】 项目下 【{}】 测试任务 (报告 id: {}) 中报错测试用例已全部恢复通过～ 最新测试报告详情内容请查阅附件 ～ \n\n   最新报告 id 为:" \
                               " {} \n\n   最新报告生成时间为: {}" \
                    .format(self.recorded_first_failed_time[self.cron_name], project_name, self.cron_name,
                            self.recorded_first_failed_report_id[self.cron_name], self.report_id,
                            self.report_created_time.strftime('%Y-%m-%d %H:%M:%S'))
                mesg_attachment_name = f'接口测试报告_{self.report_created_time.strftime("%Y-%m-%d %H:%M:%S")}.xlsx'
                mesg_attachment_content = TestReport.get_test_report_excel_bytes_io(self.report_id).read()
                result_json = self.send_report_to_staff(project_id, self.alarm_mail_list, mesg_title, mesg_content,
                                                        mesg_attachment_name, mesg_attachment_content)
                if result_json.get('status') == 'failed':
                    raise BaseException('邮件发送异常: {}'.format(result_json.get('data')))

                self.stop_alert_and_wait_until_resume[self.cron_name] = False

            elif failed_again_but_wait_for_resume:
                # 在等待中且有失败的情况，暂时不做任何操作，防止使用者被不断的定时任务提醒轰炸
                print(f'failed_again_but_wait_for_resume， report_id: {self.report_id}')
            elif not self.stop_alert_and_wait_until_resume.get(self.cron_name):
                if self.failed_count > 0:
                    self.recorded_first_failed_report_id[self.cron_name] = copy.deepcopy(self.report_id)
                    date_now = str(datetime.datetime.now())
                    dot_index = date_now.rindex('.')
                    self.recorded_first_failed_time[self.cron_name] = date_now[:dot_index]
                    self.stop_alert_and_wait_until_resume[self.cron_name] = True if self.failed_count else False

                if is_send_enterprise_wechat:

                    enterprise_wechat_title = '### 接口测试平台企业微信服务'
                    enterprise_wechat_content = f' ⛔ {project_name} 项目 \n\n > 🚑 {self.cron_name} 测试失败 \n\n' \
                                                f' > 生成报告id: {self.report_id} \n\n > ⬇️ 此时下方应有报告详情 ' \
                        if self.failed_count > 0 else f' ✅️ {project_name} 项目 \n\n > 👍️️️️ {self.cron_name} 测试通过 \n\n ' \
                                                      f'> 生成报告id: {self.report_id} \n\n > ⬇️ 此时下方应有报告详情 '
                    if hasattr(self,
                               'enterprise_wechat_notify_strategy') and self.enterprise_wechat_notify_strategy.get(
                            'fail') \
                            and self.failed_count > 0:
                        enterprise_wechat_res = self.send_enterprise_wechat_notify(title=enterprise_wechat_title,
                                                                                   content=enterprise_wechat_content)
                        if not enterprise_wechat_res.status_code == 200:
                            raise BaseException('企业微信发送异常: {}'.format(enterprise_wechat_res.text))
                    if hasattr(self,
                               'enterprise_wechat_notify_strategy') and self.enterprise_wechat_notify_strategy.get(
                            'success') \
                            and self.failed_count <= 0:
                        enterprise_wechat_res = self.send_enterprise_wechat_notify(title=enterprise_wechat_title,
                                                                                   content=enterprise_wechat_content)
                        if not enterprise_wechat_res.status_code == 200:
                            raise BaseException('企业微信发送异常: {}'.format(enterprise_wechat_res.text))

                if is_send_ding_ding:
                    dingding_title = '### 接口测试平台钉钉服务'
                    dingding_content = f' ⛔ {project_name} 项目 \n\n > 🚑 {self.cron_name} 测试失败 \n\n' \
                                       f' > 生成报告id: {self.report_id}' \
                        if self.failed_count > 0 else f' ✅️ {project_name} 项目 \n\n > 👍️️️️ {self.cron_name} 测试通过 \n\n ' \
                                                      f'> 生成报告id: {self.report_id}'
                    if hasattr(self, 'ding_ding_notify_strategy') and self.ding_ding_notify_strategy.get('fail') \
                            and self.failed_count > 0:
                        dingding_res = self.send_ding_ding_notify(title=dingding_title, content=dingding_content)
                        if not dingding_res.status_code == 200:
                            raise BaseException('钉钉发送异常: {}'.format(dingding_res.text))
                    if hasattr(self, 'ding_ding_notify_strategy') and self.ding_ding_notify_strategy.get('success') \
                            and self.failed_count <= 0:
                        dingding_res = self.send_ding_ding_notify(title=dingding_title, content=dingding_content)
                        if not dingding_res.status_code == 200:
                            raise BaseException('钉钉发送异常: {}'.format(dingding_res.text))

                if is_send_mail:
                    mesg_title = '接口测试平台告警 :('
                    mesg_content = "Dears: \n\n  【{}】 项目下 【{}】 测试任务中存在未通过的测试用例！测试报告详情内容请查阅附件 ～ \n\n   报告 id 为:" \
                                   " {} \n\n   报告生成时间为: {}" \
                        .format(project_name, self.cron_name, self.report_id,
                                self.report_created_time.strftime('%Y-%m-%d %H:%M:%S'))
                    mesg_attachment_name = f'接口测试报告_{self.report_created_time.strftime("%Y-%m-%d %H:%M:%S")}.xlsx'
                    mesg_attachment_content = TestReport.get_test_report_excel_bytes_io(self.report_id).read()
                    result_json = self.send_report_to_staff(project_id, self.alarm_mail_list, mesg_title, mesg_content,
                                                            mesg_attachment_name, mesg_attachment_content)
                    if result_json.get('status') == 'failed':
                        raise BaseException('邮件发送异常: {}'.format(result_json.get('data')))
            else:
                pass


if __name__ == '__main__':
    pass
