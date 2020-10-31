#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from utils.mango import *
from utils import common
import xlsxwriter
from io import BytesIO
import ast
import datetime
from bson import ObjectId

test_report_summary_map = {
    'projectName': '测试项目',
    'testDomain': '测试环境',
    'testCount': '用例总数',
    'passCount': '通过数',
    'failedCount': '失败数',
    'passRate': '通过率',
    'comeFrom': '报告来源',
    'executorNickName': '执行人',
    'createAt': '生成时间',
    'totalTestSpendingTimeInSec': '总耗时/s'
}

# 使用 dic_get 定位数据
test_report_detail_map = {
    "['testBaseInfo', 'name']": '用例名称',
    "['testBaseInfo', 'requestMethod']": '请求方法',
    "['testBaseInfo', 'url']": '请求地址',
    "['testBaseInfo', 'headers']": '请求头',
    "['testBaseInfo', 'cookies']": '请求Cookie',
    "['testBaseInfo', 'presendParams']": '请求参数',
    "['testBaseInfo', 'checkHttpCode']": '状态码校验',
    "['responseHttpStatusCode']": '实际状态码',
    "['testBaseInfo', 'checkResponseData']": '数据校验',
    "['testBaseInfo', 'checkResponseNumber']": '数值校验',
    "['testBaseInfo', 'checkResponseSimilarity']": '相似度校验',
    "['responseData']": '实际数据',
    "['testConclusion']": '测试结论',
    "['testStartTime']": '测试开始时间',
    "['spendingTimeInSec']": '测试耗时/s',
}


# 类名定义 collection
class TestReport(Model):

    class Meta:
        database = db
        collection = 'testReport'


    # 字段
    _id = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    projectId = ObjectIdField()
    projectName = StringField()
    testDomain = StringField()
    createAt = DateField()
    lastUpdateTime = DateField()
    totalTestSpendingTimeInSec = FloatField()
    testCount = IntField()
    passCount = IntField()
    failedCount = IntField()
    passRate = StringField()
    testDetail = ArrayField()
    comeFrom = StringField()
    executorNickName = StringField()
    cronId = StringField()

    @classmethod
    def get_test_report_excel_bytes_io(cls, report_id):
        test_report = cls.find_one({'_id': ObjectId(report_id)})
        test_report = common.format_response_in_dic(test_report)

        bytes_io = BytesIO()
        workbook = xlsxwriter.Workbook(bytes_io, {'in_memory': True})

        summary_sheet = workbook.add_worksheet(u'测试报告概览')
        detail_sheet = workbook.add_worksheet(u'测试报告详情')

        # 测试报告概览表头
        for index, value in enumerate(test_report_summary_map.values()):
            summary_sheet.write(0, index, value)

        # 测试报告概览数据
        for index, value in enumerate(test_report_summary_map.keys()):
            summary_sheet.write(1, index, str(test_report.get(value, '(暂无此数据)')))

        test_details = test_report['testDetail']

        # 测试报告详情表头
        for index, value in enumerate(test_report_detail_map.values()):
            detail_sheet.write(0, index, value)

        # 测试报告详情数据
        for index, locator in enumerate(test_report_detail_map.keys()):
            locator = ast.literal_eval(locator)
            for col_index, detail in enumerate(test_details):
                detail_sheet.write(col_index + 1, index, str(common.dict_get(detail, locator)))

        workbook.close()

        bytes_io.seek(0)

        return bytes_io

    def __str__(self):
        return "createAt:{}"\
            .format(self.createAt)


if __name__ == '__main__':
    pass
