#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *


# 类名定义 collection
class AdminUser(Model):

    class Meta:
        database = db
        collection = 'adminUser'

    # 字段

    _id = ObjectIdField()
    username = StringField(unique=True)
    password = StringField()
    nickName = StringField(unique=True)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    roleIds = ArrayField()
    createAt = DateField()
    lastUpdateTime = DateField()

    def __str__(self):
        return "username:{} - password:{} - nickName:{}"\
            .format(self.username, self.password, self.nickName)


if __name__ == '__main__':
    pass

