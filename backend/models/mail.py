#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class Mail(Model):

    class Meta:
        database = db
        collection = 'mail'


    # 字段
    name = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    _id = ObjectIdField()
    projectId = ObjectIdField()
    mailAddress = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    creatorNickName = StringField()
    lastUpdateTime = DateField()
    lastUpdatorNickName = StringField()

    def __str__(self):
        return "name:{} - email:{} - description:{} - status:{}"\
            .format(self.name, self.mailAddress, self.description, self.status)


if __name__ == '__main__':
    pass
