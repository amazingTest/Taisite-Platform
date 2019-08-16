from utils import common
from models.caseSuite import CaseSuite
from models.testingCase import TestingCase
from models.mailSender import MailSender
from testframe.interfaceTest.tester import tester
from models.testReport import TestReport
import pymongo
from bson import ObjectId
import datetime
import requests


class Cron:
    def __init__(self, test_case_suite_id_list, test_domain,  trigger_type, is_execute_forbiddened_case=False,
                 test_case_id_list=None, alarm_mail_list=None, is_ding_ding_notify=False, ding_ding_access_token=None,
                 ding_ding_notify_strategy=None, is_web_hook=False, **trigger_args):

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

        # print('self.ding_ding_access_token ----> %s' % self.ding_ding_access_token)
        # print('self.ding_ding_notify_strategy ----> %s' % self.ding_ding_notify_strategy)

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

    def generate_test_report(self, project_id, cron_id, test_result_list):

        test_count = len(test_result_list)
        passed_count = len(
            list(filter(lambda x: x == 'ok', [test_result["status"] for test_result in test_result_list])))
        failed_count = len(
            list(filter(lambda x: x == 'failed', [test_result["status"] for test_result in test_result_list])))
        passed_rate = '%d' % round((passed_count / test_count) * 100, 2) + '%'

        self.report_created_time = datetime.datetime.now()
        self.failed_count = failed_count

        execute_from = "WebHook" if hasattr(self, 'is_web_hook') and self.is_web_hook else "定时任务"

        raw_data = {
            "projectId": ObjectId(project_id),
            "testCount": test_count,
            "passCount": passed_count,
            "failedCount": failed_count,
            "passRate": passed_rate,
            "comeFrom": execute_from,
            "executorNickName": "定时机器人",
            "cronId": cron_id,
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

    # TODO 当webhook模式触发cron时，可选测试结果发送微信群
    def send_wechat_notify(self, hook_url, message):
        pass

    # TODO 发送报告具体链接至邮箱。 如interfaceTestProject/5ccfa182b144f831b04d7ca5/projectReport
    def send_report_to_staff(self, project_id, mail_list, mail_title, mail_content):
        if not isinstance(mail_list, list):
            raise TypeError("mail_list must be list!")
        if self.failed_count < 1:
            raise TypeError('测试全通过，不需要发送告警报告！')
        if not self.report_created_time:
            raise TypeError('无测试报告生成时间，报告发送失败！')

        json_data = dict()
        json_data['mail_list'] = mail_list
        json_data['mail_title'] = mail_title
        json_data['mail_content'] = mail_content

        result = common.send_email(MailSender, project_id, json_data)

        return result

    def cron_mission(self):
        cron_test_cases_list = self.get_cron_test_cases_list()
        if len(cron_test_cases_list) > 0:
            project_id = cron_test_cases_list[0]["projectId"]
        else:
            raise TypeError('定时任务执行中未找到任何可执行用例！')

        tester_for_cron = tester(test_case_list=cron_test_cases_list,
                                 domain=self.test_domain)
        test_result_list = tester_for_cron.execute_all_test_for_cron_and_single_test()

        for index, test_result in enumerate(test_result_list):
            test_result = common.format_response_in_dic(test_result)
            test_result_list[index] = test_result

        if len(test_result_list) > 0:
            self.generate_test_report(project_id, self.get_id(), test_result_list)
            is_send_mail = self.failed_count > 0 and isinstance(self.alarm_mail_list, list)\
                                   and len(self.alarm_mail_list) > 0
            is_send_ding_ding = self.ding_ding_access_token if hasattr(self, 'ding_ding_access_token') else False
            if is_send_ding_ding:
                dingding_title = '智能测试平台钉钉服务'
                dingding_content = '### ⛔️ 泰斯特平台 \n >⛔ 测试失败 \n >  生成报告id: {}'.format(self.report_id)\
                    if self.failed_count > 0 else '### ✅️ 泰斯特平台 \n >👍️️️️ 测试通过 \n >  生成报告id: {}'\
                    .format(self.report_id)
                if hasattr(self, 'ding_ding_notify_strategy') and self.ding_ding_notify_strategy.get('fail')\
                        and self.failed_count > 0:
                    dingding_res = self.send_ding_ding_notify(title=dingding_title, content=dingding_content)
                    if not dingding_res.status_code == 200:
                        raise BaseException('钉钉发送异常: {}'.format(dingding_res.text))
                if hasattr(self, 'ding_ding_notify_strategy') and self.ding_ding_notify_strategy.get('success')\
                        and self.failed_count <= 0:
                    dingding_res = self.send_ding_ding_notify(title=dingding_title, content=dingding_content)
                    if not dingding_res.status_code == 200:
                        raise BaseException('钉钉发送异常: {}'.format(dingding_res.text))
            if is_send_mail:
                mesg_title = '测试平台告警'
                mesg_content = "Dears: \n\n   定时测试中存在用例未通过！，请登录平台查看详情 ！\n\n   报告编号为:" \
                               " {} \n\n   报告生成时间为: {}"\
                    .format(self.report_id, self.report_created_time.strftime('%Y-%m-%d %H:%M:%S'))
                result_json = self.send_report_to_staff(project_id, self.alarm_mail_list, mesg_title, mesg_content)
                if result_json.get('status') == 'failed':
                    raise BaseException('邮件发送异常: {}'.format(result_json.get('data')))
        else:
            raise TypeError('无任何测试结果！')


if __name__ == '__main__':
    pass
