#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort, send_file
from models.testReport import TestReport
from bson import ObjectId
from utils import common
from flask_login import login_required


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


@app.route('/api/project/<project_id>/reportsList/<report_id>/export', methods=['POST'])
@login_required
def export_report(project_id, report_id):
    bytes_io = TestReport.get_test_report_excel_bytes_io(report_id)
    return send_file(bytes_io, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')