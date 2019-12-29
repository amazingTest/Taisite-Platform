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

    data['isExecuteForbiddenedCase'] = True if data.get('isExecuteForbiddenedCase') \
                                               and common.can_convert_to_str(data.get('isExecuteForbiddenedCase'))\
                                               and data.get('isExecuteForbiddenedCase').upper() == 'TRUE' else False

    data['isDingDingNotify'] = True if data.get('isDingDingNotify')\
                                            and common.can_convert_to_str(data.get('isDingDingNotify'))\
                                            and data.get('isDingDingNotify').upper() == 'TRUE' else False

    data['isEnterpriseWechatNotify'] = True if data.get('isEnterpriseWechatNotify')\
                                       and common.can_convert_to_str(data.get('isEnterpriseWechatNotify')) \
                                       and data.get('isEnterpriseWechatNotify').upper() == 'TRUE' else False

    data['dingdingAccessToken'] = data.get('dingdingAccessToken').strip() if data.get('dingdingAccessToken')\
                                        and common.can_convert_to_str(data.get('dingdingAccessToken')) else None

    data['enterpriseWechatAccessToken'] = data.get('enterpriseWechatAccessToken').strip()\
        if data.get('enterpriseWechatAccessToken') and common.can_convert_to_str(data.get('enterpriseWechatAccessToken')) else None

    try:
        data['alarmMailList'] = data['alarmMailList'].strip().split(';') if data.get('alarmMailList') else []
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
                is_enterprise_wechat_notify=filtered_data.get('isEnterpriseWechatNotify'),
                enterprise_wechat_access_token=filtered_data.get('enterpriseWechatAccessToken'),
                is_web_hook=True)
    cron_manager.add_cron(cron)

