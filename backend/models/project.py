#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *

# 类名定义 collection
class Project(Model):

    class Meta:
        database = db
        collection = 'project'


    # 字段
    name = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    _id = ObjectIdField()
    version = StringField()
    description = StringField()
    projectTestType = StringField()
    status = BooleanField(field_name='status', default=True)
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    # 性能测试字段
    loopNum = IntField()
    mailList = ArrayField()
    domain = StringField()


    def __str__(self):
        return "name:{} - description:{} - projectTestType:{} - status:{}"\
            .format(self.name, self.description, self.projectTestType, self.status)


if __name__ == '__main__':
    pass