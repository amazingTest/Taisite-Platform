#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class TestingCase(Model):

    class Meta:
        database = db
        collection = 'testingCase'

    # 字段
    name = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    _id = ObjectIdField()
    description = StringField()

    projectId = ObjectIdField()
    originApiSuiteId = ObjectIdField()
    originApiId = ObjectIdField()
    caseSuiteId = ObjectIdField()
    originTestingCaseIds = ArrayField(field_name='originTestingCaseIds', default=[])

    presendParams = DictField(field_name='presendParams', default={})
    testCaseType = StringField()
    setGlobalVars = ArrayField(field_name='setGlobalVars', default=[{'name': '', 'query': []}],
                               expected_structure={'expectedTypeRange': [list],
                                                   'expectedValueRange': [{
                                                       'expectedTypeRange': [dict],
                                                       'expectedDict': {
                                                           'name': {'expectedTypeRange': [str]},
                                                           'query': {
                                                               'expectedTypeRange': [list],
                                                               'expectedValueRange':[
                                                                   {'expectedTypeRange': [str]}
                                                               ]
                                                           }
                                                       }
                                                   }]})
    testStatus = BooleanField(field_name='testStatus', default=False)  # 测试状态，true 代表测试进行中
    lastManualTestResult = DictField(field_name='lastManualTestResult', default={})
    requestProtocol = StringField()
    requestMethod = StringField()
    domain = StringField()  # 优先级最高
    route = StringField()
    headers = ArrayField(field_name='headers',
                         default=[{'name': 'Accept', 'value': 'application/json'},
                                  {'name': 'Content-Type', 'value': 'application/json'}],
                         expected_structure={'expectedTypeRange': [list],
                                             'expectedValueRange': [{
                                                 'expectedTypeRange': [dict],
                                                 'expectedDict': {
                                                     'name': {'expectedTypeRange': [str]},
                                                     'value': {'expectedTypeRange': [str]}
                                                 }
                                             },
                                             {
                                                 'expectedTypeRange': [dict],
                                                 'expectedDict': {
                                                     'interrelate': {'expectedTypeRange': []},
                                                     'name': {'expectedTypeRange': [str]},
                                                     'value': {'expectedTypeRange': []}
                                                 }
                                             },
                                             ]}
                         )
    status = BooleanField(field_name='status', default=False)
    isClearCookie = BooleanField(field_name='isClearCookie', default=False)
    checkHttpCode = StringField()
    checkResponseData = ArrayField(field_name='checkResponseData', default=[{'regex': '', 'query': []}],
                                   expected_structure={'expectedTypeRange': [list, type(None)],
                                                       'expectedValueRange': [{
                                                           'expectedTypeRange': [dict],
                                                           'expectedDict': {
                                                               'regex': {'expectedTypeRange': [str]},
                                                               'query': {
                                                                   'expectedTypeRange': [list],
                                                                   'expectedValueRange': [
                                                                       {'expectedTypeRange': [str]}
                                                                   ]
                                                               }
                                                           }
                                                       }]}
                                   )
    checkResponseSimilarity = ArrayField(
        field_name='checkResponseSimilarity',
        default=[{"baseText": "", "compairedText": "", "targetSimilarity": None}],
        expected_structure={'expectedTypeRange': [list, type(None)],
                            'expectedValueRange': [
                                {
                                    'expectedTypeRange': [dict],
                                    'expectedDict': {
                                        'baseText': {'expectedTypeRange': [str]},
                                        'compairedText': {'expectedTypeRange': [str]},
                                        'targetSimilarity': {'expectedTypeRange': [type(None), int, float, str]}
                                    }
                                }
                            ]})
    checkResponseNumber = ArrayField(
        field_name='checkResponseNumber',
        default=[{"expressions":
                  {
                      'firstArg': '',
                      'operator': '',
                      'secondArg': '',
                      'judgeCharacter': '',
                      'expectResult': ''
                  }
                  }],
        expected_structure={'expectedTypeRange': [list, type(None)],
                            'expectedValueRange': [{
                                'expectedTypeRange': [dict],
                                'expectedDict': {
                                    'expressions': {
                                        'expectedTypeRange': [dict],
                                        'expectedDict':{
                                            'firstArg': {'expectedTypeRange': [str]},
                                            'operator': {'expectedTypeRange': [str]},
                                            'secondArg': {'expectedTypeRange': [str]},
                                            'judgeCharacter': {'expectedTypeRange': [str]},
                                            'expectResult': {'expectedTypeRange': [str]}
                                        }
                                    }
                                }
                            }]}
    )
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    def __str__(self):
        return "name:{}"\
            .format(self.name)


if __name__ == '__main__':
    pass

