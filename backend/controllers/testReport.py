#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort, send_file
from models.testReport import TestReport
from bson import ObjectId
from utils import common
from flask_login import login_required
import xlsxwriter
from io import BytesIO
import ast


@app.route('/api/project/<project_id>/reportsList', methods=['GET', 'POST'])
@login_required
def reports_list(project_id):
    # TODO 性能优化
    total_num, test_reports = common.get_total_num_and_arranged_data(TestReport, request.args)
    for test_report in test_reports:
        del test_report['testDetail']
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': test_reports}})


@app.route('/api/project/<project_id>/reportsList/<report_id>', methods=['GET'])
@login_required
def report_detail(project_id, report_id):
    test_report = TestReport.find_one({'_id': ObjectId(report_id)})
    test_report = common.format_response_in_dic(test_report)
    return jsonify({'status': 'ok', 'data': test_report}) if test_report else \
        jsonify({'status': 'failed', 'data': '未找到报告详情'})


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


@app.route('/api/project/<project_id>/reportsList/<report_id>/export', methods=['POST'])
@login_required
def export_report(project_id, report_id):

    test_report = TestReport.find_one({'_id': ObjectId(report_id)})
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
    return send_file(bytes_io, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')