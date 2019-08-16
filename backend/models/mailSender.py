#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class MailSender(Model):

    class Meta:
        database = db
        collection = 'mailSender'


    # 字段
    username = StringField()
    password = StringField()
    _id = ObjectIdField()
    projectId = ObjectIdField()
    createAt = DateField()
    status = BooleanField(field_name='status', default=True)
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

if __name__ == '__main__':
    pass