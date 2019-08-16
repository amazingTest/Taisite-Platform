from app import app
from github_webhook import Webhook
from utils.cron.interfaceTestCron import Cron
from models.cronTab import CronTab
from app import cron_manager
from utils import common
import datetime
webhook = Webhook(app, endpoint='/api/webhook')


@webhook.hook(event_type='ExecTest')        # Defines a handler for the 'ExecTest' event
def on_exec_test(data):
    try:
        data['testCaseSuiteIdList'] = data['testCaseSuiteIdList'].strip().split(';')
    except BaseException:
        raise TypeError('参数 「testCaseSuiteIdList」 不合法')

    try:
        data['testDomain'] = data['testDomain'].strip()
    except BaseException:
        raise TypeError('参数 「testDomain」 不合法')

    try:
        data['dingdingAccessToken'] = data['dingdingAccessToken'].strip()
    except BaseException:
        raise TypeError('参数 「dingdingAccessToken」 不合法')

    data['isExecuteForbiddenedCase'] = True if common.can_convert_to_str(data.get('isExecuteForbiddenedCase'))\
                                               and data.get('isExecuteForbiddenedCase').upper() == 'TRUE' else False

    data['isDingDingNotify'] = True if common.can_convert_to_str(data.get('isDingDingNotify'))\
                                               and data.get('isDingDingNotify').upper() == 'TRUE' else False

    try:
        data['alarmMailList'] = data['alarmMailList'].strip().split(';')
    except BaseException:
        raise TypeError('参数 「alarmMailList」 不合法')

    data["testCaseIdList"] = []
    data['triggerType'] = "date"
    data['runDate'] = datetime.datetime.now()  # 瞬间触发
    filtered_data = CronTab.filter_field(data, use_set_default=True)
    cron = Cron(test_case_suite_id_list=filtered_data.get('testCaseSuiteIdList'),
                test_domain=filtered_data.get('testDomain'),
                alarm_mail_list=filtered_data.get('alarmMailList'),
                trigger_type=filtered_data.get('triggerType'),
                test_case_id_list=filtered_data.get('testCaseIdList'),
                is_execute_forbiddened_case=filtered_data.get('isExecuteForbiddenedCase'),
                run_date=filtered_data.get('runDate'),
                is_ding_ding_notify=filtered_data.get('isDingDingNotify'),
                ding_ding_access_token=filtered_data.get('dingdingAccessToken'),
                is_web_hook=True)
    cron_manager.add_cron(cron)

