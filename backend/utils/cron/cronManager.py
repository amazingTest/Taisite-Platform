from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from utils.cron.interfaceTestCron import Cron
from utils import common
from pytz import timezone
shanghai_tz = timezone('Asia/Shanghai')
from app import db
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger


class CronManager:

    def __init__(self, use_mongo_db=True):

        self.scheduler = BackgroundScheduler(timezone=shanghai_tz)
        self.scheduler.configure()

        if use_mongo_db:
            self.job_store = MongoDBJobStore(database='apscheduler', collection='cronTab', client=db)
            self.scheduler.add_jobstore(self.job_store)
            self.is_replace_existing = True
        else:
            self.is_replace_existing = False

    def add_cron(self, cron_instance):
        if not isinstance(cron_instance, Cron):
            raise TypeError('please add correct cron！')

        if cron_instance.trigger_type == 'interval':
            seconds = cron_instance.trigger_args.get('seconds')
            if not isinstance(seconds, int) and not common.can_convert_to_int(seconds):
                raise TypeError('请输入合法的时间间隔！')
            seconds = int(seconds)
            if seconds <= 0:
                raise TypeError('请输入大于0的时间间隔！')
            job = self.scheduler.add_job(func=cron_instance.cron_mission,
                                         trigger=cron_instance.trigger_type,
                                         seconds=seconds,
                                         replace_existing=self.is_replace_existing,
                                         coalesce=True,
                                         id=cron_instance.get_id(),
                                         max_instances=5,
                                         jitter=0)  # 玄学，新增job的时候不用加args，直接加对象调用的func
        elif cron_instance.trigger_type == 'date':
            run_date = cron_instance.trigger_args.get('run_date')
            # TODO 判断run_date类型
            job = self.scheduler.add_job(func=cron_instance.cron_mission,
                                         trigger=cron_instance.trigger_type,
                                         run_date=run_date,
                                         replace_existing=self.is_replace_existing,
                                         coalesce=True,
                                         id=cron_instance.get_id())  # 玄学，新增job的时候不用加args，直接加对象调用的func
        elif cron_instance.trigger_type == 'cron':
            raise TypeError('暂时不支持 trigger_type 等于 \'cron\'')

        return cron_instance.get_id()

    def start(self, paused=False):
        self.scheduler.start(paused=paused)

    def pause_cron(self, cron_id=None, pause_all=False):
        if pause_all:
            self.scheduler.pause()
        elif cron_id:
            self.scheduler.pause_job(job_id=cron_id)

    def resume_cron(self, cron_id=None, resume_all=False):
        if resume_all:
            self.scheduler.resume()
        elif cron_id:
            self.scheduler.resume_job(job_id=cron_id)

    def del_cron(self, cron_id=None, del_all=False):
        if del_all:
            self.scheduler.remove_all_jobs()
        elif cron_id:
            self.scheduler.remove_job(job_id=cron_id)

    def update_cron(self, cron_id, cron_info):
        if not isinstance(cron_id, str):
            raise TypeError('cron_id must be str')

        if not isinstance(cron_info, dict):
            raise TypeError('cron_info must be dict')

        trigger_type = cron_info.get('triggerType')
        interval = cron_info.get('interval')
        run_date = cron_info.get('runDate')
        test_case_suite_id_list = cron_info.get('testCaseSuiteIdList')
        is_execute_forbiddened_case = cron_info.get('isExecuteForbiddenedCase')
        test_case_id_list = cron_info.get('testCaseIdList')
        test_domain = cron_info.get('testDomain')
        alarm_mail_list = cron_info.get('alarmMailList')
        is_ding_ding_notify = cron_info.get('isDingDingNotify')
        ding_ding_access_token = cron_info.get('dingdingAccessToken')
        ding_ding_notify_strategy = cron_info.get('dingdingNotifyStrategy')

        try:
            if trigger_type == 'interval' and int(interval) > 0:
                self.scheduler.modify_job(job_id=cron_id, trigger=IntervalTrigger(seconds=interval))
            elif trigger_type == 'date':
                # TODO 判断run_date类型
                self.scheduler.modify_job(job_id=cron_id, trigger=DateTrigger(run_date=run_date))
            else:
                raise TypeError('更新定时任务触发器失败！')
            if run_date:
                cron = Cron(test_case_suite_id_list=test_case_suite_id_list,
                            is_execute_forbiddened_case=is_execute_forbiddened_case,
                            test_domain=test_domain,
                            alarm_mail_list=alarm_mail_list,
                            is_ding_ding_notify=is_ding_ding_notify,
                            ding_ding_access_token=ding_ding_access_token,
                            ding_ding_notify_strategy=ding_ding_notify_strategy,
                            trigger_type=trigger_type,  # 更新定时器时，此参数并没有真正起到作用, 仅修改展示字段
                            test_case_id_list=test_case_id_list,
                            run_date=run_date)  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
            else:
                cron = Cron(test_case_suite_id_list=test_case_suite_id_list,
                            is_execute_forbiddened_case=is_execute_forbiddened_case,
                            test_domain=test_domain,
                            alarm_mail_list=alarm_mail_list,
                            is_ding_ding_notify=is_ding_ding_notify,
                            ding_ding_access_token=ding_ding_access_token,
                            ding_ding_notify_strategy=ding_ding_notify_strategy,
                            trigger_type=trigger_type,  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
                            test_case_id_list=test_case_id_list,
                            seconds=interval)  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
            # 玄学，更改job的时候必须改args，不能改func
            self.scheduler.modify_job(job_id=cron_id, coalesce=True, args=[cron])

        except BaseException as e:
            raise TypeError('更新定时任务失败: %s' % e)

    def shutdown(self, force_shutdown=False):
        if force_shutdown:
            self.scheduler.shutdown(wait=False)
        else:
            self.scheduler.shutdown(wait=True)

    def get_crons(self):
        return self.scheduler.get_jobs()


if __name__ == '__main__':
    pass




