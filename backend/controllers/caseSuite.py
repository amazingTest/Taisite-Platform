#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort
from models.caseSuite import CaseSuite
from models.testingCase import TestingCase
from bson import ObjectId
from utils import common
import datetime
from flask_login import login_required


# 管理测试项目中的接口用例组信息
@app.route('/api/project/<project_id>/caseSuiteList', methods=['GET', 'POST'])
@login_required
def case_suite_list(project_id):
    total_num, case_suites = common.get_total_num_and_arranged_data(CaseSuite, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': case_suites}})


@app.route('/api/project/<project_id>/addCaseSuite', methods=['POST'])
@login_required
def add_case_suite(project_id):
    request_data = request.get_json()
    request_data["status"] = True
    request_data["projectId"] = ObjectId(project_id)
    request_data["lastUpdateTime"] = datetime.datetime.utcnow()
    request_data["createAt"] = datetime.datetime.utcnow()

    try:
        filtered_data = CaseSuite.filter_field(request.get_json(), use_set_default=True)
        CaseSuite.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '添加失败 %s' % e})


@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/copyCaseSuite', methods=['POST'])
@login_required
def copy_case_suite(project_id, case_suite_id):
    try:
        test_case_suite = list(CaseSuite.find({'_id': ObjectId(case_suite_id)}))[0]
        test_case_suite['originCaseSuiteIds'] = [] if 'originCaseSuiteIds' not in test_case_suite \
            else test_case_suite['originCaseSuiteIds']
        origin_case_suite_id_info = dict()
        origin_case_suite_id_info['_id'] = test_case_suite.pop('_id') if test_case_suite.get('_id') else None
        origin_case_suite_id_info['copiedAt'] = datetime.datetime.utcnow()
        test_case_suite['originCaseSuiteIds'].append(origin_case_suite_id_info)

        def get_new_create_at(create_at):
            time_quantity = 1
            while True:
                new_create_at = create_at - datetime.timedelta(milliseconds=time_quantity)
                find_result = list(CaseSuite.find({'createAt': new_create_at}))
                has_identical_create_at_case_suite = True if len(find_result) > 0 else False
                if not has_identical_create_at_case_suite:
                    return new_create_at
                else:
                    time_quantity += 1

        case_suite_create_at = test_case_suite.get('createAt')
        new_case_suite_create_at = get_new_create_at(case_suite_create_at)  # 超前插入，精髓
        new_case_suite_suffix = '(复制版)'
        case_suite_name = test_case_suite.pop('name') + new_case_suite_suffix \
            if 'name' in test_case_suite else '未知用例组' + new_case_suite_suffix
        test_case_suite['createAt'] = new_case_suite_create_at
        test_case_suite['name'] = case_suite_name
        new_case_suite_id = CaseSuite.insert(test_case_suite)

        query = {'caseSuiteId': ObjectId(case_suite_id), 'isDeleted': {'$ne': True}}
        test_cases = list(TestingCase.find(query))

        def substitute_info(testing_case):
            testing_case['originTestingCaseIds'] = [] if 'originTestingCaseIds' not in testing_case \
                else testing_case['originTestingCaseIds']
            origin_testing_case_id_info = dict()
            origin_testing_case_id_info['_id'] = testing_case.pop('_id') if testing_case.get('_id') else None
            origin_testing_case_id_info['copiedAt'] = datetime.datetime.utcnow()
            testing_case['originTestingCaseIds'].append(origin_testing_case_id_info)
            testing_case['caseSuiteId'] = new_case_suite_id
            return testing_case

        substituted_test_cases = list(map(substitute_info, test_cases))
        for substituted_test_case in substituted_test_cases:
            TestingCase.insert(substituted_test_case)
        return jsonify({'status': 'ok', 'data': '复制成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '复制失败 %s' % e})


@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/updateCaseSuite', methods=['POST'])
@login_required
def update_case_suite(project_id, case_suite_id):
    try:
        filtered_data = CaseSuite.filter_field(request.get_json())
        for key, value in filtered_data.items():
            CaseSuite.update({"_id": ObjectId(case_suite_id)},
                        {'$set': {key: value}})
        update_response = CaseSuite.update({"_id": ObjectId(case_suite_id)},
                    {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}},)
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


