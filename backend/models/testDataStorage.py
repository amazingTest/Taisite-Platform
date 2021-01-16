#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class TestDataStorage(Model):

    class Meta:
        database = db
        collection = 'testDataStorage'


    # 字段

    name = StringField()
    description = StringField()

    # dataMap = ArrayField(field_name='dataMap', default=[{'key': '', 'value': '', '__value_type': ''}],
    #                        expected_structure={'expectedTypeRange': [list],
    #                                            'expectedValueRange': [{
    #                                                'expectedTypeRange': [dict],
    #                                                'expectedDict': {
    #                                                    'key': {'expectedTypeRange': [str]},
    #                                                    'value': {'expectedTypeRange': [str, dict, list, int, float, bool]},
    #                                                    '__value_type': {'expectedTypeRange': [str]},
    #                                                }
    #                                            }]
    #                                         })

    dataMap = DictField()
    _id = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    projectId = ObjectIdField()
    createAt = DateField()
    status = BooleanField(field_name='status', default=True)
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()


if __name__ == '__main__':
    pass