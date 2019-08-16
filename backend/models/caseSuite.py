#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class CaseSuite(Model):

    class Meta:
        database = db
        collection = 'caseSuite'


    # 字段
    name = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    _id = ObjectIdField()
    projectId = ObjectIdField()
    originApiSuiteId = ObjectIdField()
    originCaseSuiteIds = ArrayField(field_name='originCaseSuiteIds', default=[])
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    originApiId = ObjectIdField()
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    def __str__(self):
        return "name:{}"\
            .format(self.name)


if __name__ == '__main__':
    pass