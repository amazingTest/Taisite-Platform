#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class TestReport(Model):

    class Meta:
        database = db
        collection = 'testReport'


    # 字段
    _id = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    projectId = ObjectIdField()
    createAt = DateField()
    lastUpdateTime = DateField()
    testCount = IntField()
    passCount = IntField()
    failedCount = IntField()
    passRate = StringField()
    testDetail = ArrayField()
    comeFrom = StringField()
    executorNickName = StringField()
    cronId = StringField()

    def __str__(self):
        return "createAt:{}"\
            .format(self.createAt)


if __name__ == '__main__':
    pass
