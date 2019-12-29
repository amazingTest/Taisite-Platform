#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
#
class CronTab(Model):

    class Meta:
        database = db
        collection = 'apscheduler.cronTab'


    # 字段
    _id = StringField()
    projectId = ObjectIdField()
    name = StringField()
    description = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    isExecuteForbiddenedCase = BooleanField(field_name='isExecuteForbiddenedCase', default=False)
    testCaseSuiteIdList = ArrayField()
    testCaseIdList = ArrayField()
    testDomain = StringField()
    next_run_time = FloatField()
    triggerType = StringField()
    interval = FloatField()
    runDate = DateField()
    alarmMailList = ArrayField()
    isDingDingNotify = BooleanField(field_name='isDingDingNotify', default=False)
    dingdingAccessToken = StringField()
    dingdingNotifyStrategy = DictField(field_name='dingdingNotifyStrategy',
                                       default={'success': True, 'fail': True},
                                       expected_structure={
                                           'expectedTypeRange': [dict],
                                           'expectedDict': {
                                               'success': {'expectedTypeRange': [bool]},
                                               'fail': {'expectedTypeRange': [bool]}
                                           }
                                       })
    isEnterpriseWechatNotify = BooleanField(field_name='isEnterpriseWechatNotify', default=False)
    enterpriseWechatAccessToken = StringField()
    enterpriseWechatNotifyStrategy = DictField(field_name='enterpriseWechatNotifyStrategy',
                                       default={'success': True, 'fail': True},
                                       expected_structure={
                                           'expectedTypeRange': [dict],
                                           'expectedDict': {
                                               'success': {'expectedTypeRange': [bool]},
                                               'fail': {'expectedTypeRange': [bool]}
                                           }
                                       })
    status = StringField(field_name='status', default='CREATED')
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    def __str__(self):
        return "_id:{}"\
            .format(self._id)


if __name__ == '__main__':
    pass
