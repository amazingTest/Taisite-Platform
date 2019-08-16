#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class Host(Model):

    class Meta:
        database = db
        collection = 'host'


    # 字段
    name = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    _id = ObjectIdField()
    projectId = ObjectIdField()
    host = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    def __str__(self):
        return "name:{} - host:{} - description:{} - status:{}"\
            .format(self.name, self.description, self.description, self.status)


if __name__ == '__main__':
    pass