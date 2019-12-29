#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort, send_file
import xlsxwriter
import xlrd
import ast
import json
from io import BytesIO
from models.testingCase import TestingCase
from models.caseSuite import CaseSuite
from models.testReport import TestReport
from bson import ObjectId
from utils import common
import pymongo
from flask_login import login_required
import copy
import datetime


@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/caseList', methods=['GET'])
@login_required
def case_list(project_id, case_suite_id):
    total_num, testing_cases = common.get_total_num_and_arranged_data(TestingCase, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': testing_cases}})


@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/addCase', methods=['POST'])
@login_required
def add_case(project_id, case_suite_id):
    request_data = request.get_json()
    request_data["status"] = True
    request_data["caseSuiteId"] = ObjectId(case_suite_id)
    request_data["projectId"] = ObjectId(project_id)
    request_data["testCaseType"] = 'interfaceTest'
    request_data["createAt"] = datetime.datetime.utcnow()
    request_data["lastUpdateTime"] = datetime.datetime.utcnow()
    filtered_data = TestingCase.filter_field(request_data, use_set_default=True)
    try:
        TestingCase.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '添加失败 %s' % e})


# 可间接实现插入用例(改变用例组中用例执行顺序)的需求୧(๑•̀◡•́๑)૭
@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/caseList/<case_id>/copyCase', methods=['POST'])
@login_required
def copy_case(project_id, case_suite_id, case_id):
    try:
        test_case = list(TestingCase.find({'_id': ObjectId(case_id)}))[0]
        test_case.pop('_id') if test_case.get('_id') else None
        test_case_create_at = test_case.pop('createAt') if 'createAt' in test_case else datetime.datetime.utcnow()

        def get_new_create_at(create_at):
            time_quantity = 1
            while True:
                new_create_at = create_at - datetime.timedelta(milliseconds=time_quantity)
                find_result = list(TestingCase.find({'createAt': new_create_at}))
                has_identical_create_at_case = True if len(find_result) > 0 else False
                if not has_identical_create_at_case:
                    return new_create_at
                else:
                    time_quantity += 1

        new_test_case_create_at = get_new_create_at(test_case_create_at)  # 超前插入，精髓
        new_case_name_suffix = '(复制版)'
        new_case_name = test_case.pop('name') + new_case_name_suffix \
            if 'name' in test_case else '未知接口用例' + new_case_name_suffix
        test_case['createAt'] = new_test_case_create_at
        test_case['name'] = new_case_name
        TestingCase.insert(test_case)
        return jsonify({'status': 'ok', 'data': '复制成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '复制失败 %s' % e})


@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/caseList/<case_id>/updateCase', methods=['POST'])
@login_required
def update_case(project_id, case_suite_id, case_id):
    if request.get_json().get('presendParams') is not None:
        if isinstance(request.get_json().get('presendParams'), str) and \
                request.get_json().get('presendParams').strip() == '':
            request.get_json()['presendParams'] = {}
        else:
            try:
                request.get_json()['presendParams'] = request.get_json()['presendParams'].replace('\'', '\"')
                request.get_json()['presendParams'] = json.loads(request.get_json()['presendParams'])
                if not isinstance(request.get_json()['presendParams'], dict):
                    return jsonify({'status': 'failed', 'data': '请求参数数据格式不正确!'})
            except BaseException as e:
                return jsonify({'status': 'failed', 'data': '请求参数数据格式不正确!: %s' % e})

    try:
        filtered_data = TestingCase.filter_field(request.get_json())
        for key, value in filtered_data.items():
            TestingCase.update({"_id": ObjectId(case_id)},
                               {'$set': {key: value}})
        update_response = TestingCase.update({"_id": ObjectId(case_id)},
                           {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


# 管理测试项目中的接口信息
@app.route('/api/project/<project_id>/caseSuiteList/<case_suite_id>/caseList/<case_id>', methods=['GET', 'POST'])
@login_required
def case_detail(project_id, case_suite_id, case_id):
    test_case = list(TestingCase.find({'_id': ObjectId(case_id)}))
    test_case = common.format_response_in_dic(test_case[0])
    return jsonify({'status': 'ok', 'data': test_case}) if test_case else \
        jsonify({'status': 'failed', 'data': '未找到用例详情'})


@app.route('/api/startInterfaceTesting', methods=['POST'])
@login_required
def start_test():
    # TODO 性能优化
    from testframe.interfaceTest.tester import tester
    request_data = request.get_json()
    case_suite_id_list = None
    case_id_list = None
    executor_nick_name = None
    execution_mode = None
    is_single_test = None

    if 'domain' not in request_data:
        return jsonify({'status': 'failed', 'data': '缺失domain字段！'})
    else:
        domain = request_data["domain"]

    if 'caseSuiteIdList' in request_data:
        case_suite_id_list = request_data["caseSuiteIdList"]

    if 'caseIdList' in request_data:
        case_id_list = request_data["caseIdList"]

    if 'executorNickName' in request_data:
        executor_nick_name = request_data["executorNickName"]

    if 'executionMode' in request_data:
        execution_mode = request_data["executionMode"]

    testing_case_list = []
    testing_cases = copy.deepcopy(TestingCase.find({'isDeleted': {'$ne': True}, 'status': True})  # sort吃顺序
                                  .sort([('caseSuiteId', pymongo.ASCENDING), ('createAt', pymongo.ASCENDING)]))

    if case_suite_id_list:
        for case_suite_id in case_suite_id_list:
            is_forbiddened_case_suite = len(list(CaseSuite.find({'_id': ObjectId(case_suite_id),
                                                                 'status': {'$ne': True}}))) > 0
            if is_forbiddened_case_suite:
                return jsonify({'status': 'failed', 'data': '请先「启用」测试用例'})

        for testing_case in testing_cases:
            if "caseSuiteId" in testing_case and str(testing_case["caseSuiteId"]) in case_suite_id_list:
                testing_case_list.append(testing_case)

    if not case_id_list and len(testing_case_list) < 1:
        return jsonify({'status': 'failed', 'data': '未在「测试用例」中找到任何「启用的」接口测试用例'})

    testing_cases = copy.deepcopy(TestingCase.find({'isDeleted': {'$ne': True}, 'status': True})  # sort吃顺序
                                  .sort([('caseSuiteId', pymongo.ASCENDING), ('createAt', pymongo.ASCENDING)]))  # 再次初始化 Cursor object
    if case_id_list:
        for testing_case in testing_cases:
            if str(testing_case["_id"]) in case_id_list:
                testing_case_list.append(testing_case)

    if len(testing_case_list) > 0:
        project_id = testing_case_list[0]["projectId"]
    else:
        return jsonify({'status': 'failed', 'data': '请先「启用」接口测试用例'})

    # 去除相同的测试用例
    def remove_duplicated_case(case_list):
        id_list = []
        for case in case_list:
            case_id = case["_id"]
            if case_id in id_list:
                case_list.remove(case)
            else:
                id_list.append(case_id)
        return case_list

    testing_case_list = remove_duplicated_case(testing_case_list)

    if 'caseSuiteIdList' not in request_data and len(testing_case_list) == 1:
        is_single_test = True

    tester = tester(test_case_list=testing_case_list, domain=domain)

    if not is_single_test:
        try:
            tester.execute_all_test_and_send_report(TestingCase, TestReport, project_id, executor_nick_name, execution_mode)
            return jsonify({'status': 'ok', 'data': '测试已启动，稍后请留意自动化测试报告'})
        except BaseException as e:
            return jsonify({'status': 'failed', 'data': '测试启动失败: %s' % e})
    else:
        # TODO 单个接口测试需要返回测试结果，使用同步方法， 需重构
        test_result_list = tester.execute_all_test_for_cron_and_single_test()
        for index, test_result in enumerate(test_result_list):
            test_case_id = test_result["_id"]
            test_result = common.format_response_in_dic(test_result)
            test_result_list[index] = test_result
            TestingCase.update({"_id": ObjectId(test_case_id)},
                               {'$set': {'lastManualTestResult': test_result}})
        test_count = len(test_result_list)
        passed_count = len(
            list(filter(lambda x: x == 'ok', [test_result["status"] for test_result in test_result_list])))
        failed_count = len(
            list(filter(lambda x: x == 'failed', [test_result["status"] for test_result in test_result_list])))
        passed_rate = '%d' % round((passed_count / test_count) * 100, 2) + '%'

        if test_count > 0:
            for test_result in test_result_list:
                if 'testBaseInfo' in test_result and 'lastManualTestResult' in test_result['testBaseInfo']:
                    test_result['testBaseInfo'].pop('lastManualTestResult')

            raw_data = {
                "projectId": ObjectId(project_id),
                "testCount": test_count,
                "passCount": passed_count,
                "failedCount": failed_count,
                "passRate": passed_rate,
                "comeFrom": execution_mode,
                "executorNickName": executor_nick_name,
                "testDetail": test_result_list,
                "createAt": datetime.datetime.utcnow()
            }
            filtered_data = TestReport.filter_field(raw_data, use_set_default=True)
            TestReport.insert(
                filtered_data
            )

        return jsonify({'status': 'ok', 'data': test_result_list})


@app.route('/api/getLastSingleTestResult/<case_id>', methods=['get'])
@login_required
def single_test_result(case_id):
    testing_case = TestingCase.find_one({"_id": ObjectId(case_id)})
    try:
        last_execution_record = testing_case["lastManualTestResult"]
        return jsonify({'status': 'ok', 'data': last_execution_record})
    except KeyError as e:
        print(e)
        return jsonify({'status': 'ok', 'data': {}})


test_case_map = {
        'caseSuiteId': '用例组_id',
        'caseSuiteName': '用例组名称',
        '_id': '用例_id',
        'name': '用例名称',
        'description': '用例描述',
        'testCaseType': '用例类型',
        'requestProtocol': '请求协议',
        'requestMethod': '请求方法',
        'domain': '请求域名',
        'route': '请求路由',
        'headers': '请求头部',
        'presendParams': '请求参数',
        'checkHttpCode': '状态码校验',
        'checkResponseData': '正则校验',
        'checkResponseSimilarity': '文本相似度校验',
        'checkResponseNumber': '数值校验',
        'setGlobalVars': '设置全局变量',
        'isClearCookie': '请求前是否清除Cookie',
        'createAt': '创建时间/UTC',
        'creatorNickName': '创建人',
        'lastUpdateTime': '最后更新时间/UTC',
        'lastUpdatorNickName': '最后更新人',
    }


@app.route("/api/importTestCases", methods=['POST'])
@login_required
def import_test_cases():
    file = request.files.get('file')
    request_data = request.form
    case_suite_id = request_data.get('caseSuiteId') if request_data else None
    project_id = request_data.get('projectId') if request_data else None
    current_user_name = request_data.get('userName') if request_data else None

    if file is None or project_id is None or current_user_name is None:
        return jsonify({'status': 'failed', 'data': '参数不合法！值为: None'})

    if case_suite_id == 'undefined' or project_id == 'undefined' or current_user_name == 'undefined':
        return jsonify({'status': 'failed', 'data': '参数不合法！值为: undefined'})

    try:
        file_content = file.read()
        workbook = xlrd.open_workbook(file_contents=file_content)
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '「Excel」读取失败! %s' % e})

    if '测试用例' not in workbook.sheet_names():
        return jsonify({'status': 'failed', 'data': '「Excel」缺失「测试用例」Sheet'})

    test_case_table = workbook.sheet_by_name('测试用例')
    rows_num = test_case_table.nrows  # 获取该sheet中的有效行数

    if rows_num < 2:
        return jsonify({'status': 'failed', 'data': '「测试用例」Sheet 有效行数小于两行: %s 行' % rows_num})

    test_case_attributes = test_case_table.row_values(0)

    non_intersection = list(set(test_case_map.values()) ^ set(test_case_attributes))
    if non_intersection:
        missing_attributes = [nip for nip in non_intersection if nip in test_case_map.values()]
        return jsonify({'status': 'failed', 'data': '「测试用例」Sheet 表头缺失字段: %s' % missing_attributes}) \
            if missing_attributes else jsonify({'status': 'failed', 'data': '「测试用例」Sheet 表头存在多余字段: %s' %
                                               [nip for nip in non_intersection if nip not in test_case_map.values()]})

    attributes_indexes = [test_case_attributes.index(v) for v in test_case_map.values()]

    def get_pre_import_case_info(case_info, test_case_mapping, table_row_index):
        _is_case_exist, _case_info, _is_case_suite_exist = \
            common.validate_and_pre_process_import_test_case(CaseSuite, TestingCase, case_info,
                                                             test_case_mapping, table_row_index)
        return _is_case_exist, _case_info, _is_case_suite_exist

    results = []
    import_count = 0
    update_count = 0
    test_case_info = copy.deepcopy(test_case_map)
    for i in range(rows_num - 1):
        for j, v in enumerate(test_case_info.keys()):
            test_case_info[v] = test_case_table.row_values(i + 1)[attributes_indexes[j]]
        try:
            is_case_exist, pre_import_case_info, is_case_suite_exist\
                = get_pre_import_case_info(test_case_info, test_case_mapping=test_case_map, table_row_index=(i+2))
        except BaseException as b_e:
            return jsonify({'status': 'failed', 'data': '导入数据异常: %s' % b_e})

        try:
            # 在接口用例列表中导入
            if case_suite_id:
                if is_case_exist and str(pre_import_case_info.get('caseSuiteId')) == str(case_suite_id):
                    pre_import_case_info = TestingCase.filter_field(pre_import_case_info, use_set_default=False)
                    result = str(TestingCase.update({"_id": ObjectId(pre_import_case_info.get('_id'))},
                                                    {'$set': pre_import_case_info})) + \
                                                     ' _id: {}'.format(pre_import_case_info.get('_id'))
                    update_count += 1
                else:
                    try:
                        pre_import_case_info.pop('_id')
                    except BaseException:
                        pass
                    pre_import_case_info['status'] = True
                    pre_import_case_info['caseSuiteId'] = ObjectId(case_suite_id)
                    pre_import_case_info['projectId'] = ObjectId(project_id)
                    pre_import_case_info['creatorNickName'] = current_user_name
                    pre_import_case_info['lastUpdatorNickName'] = current_user_name
                    pre_import_case_info = TestingCase.filter_field(pre_import_case_info, use_set_default=True)
                    result = TestingCase.insert(pre_import_case_info)
                    import_count += 1
            # 在用例列表内导入
            else:
                inserted_case_suite_id = None
                case_suite_name = pre_import_case_info.get('caseSuiteName')\
                    if pre_import_case_info.get('caseSuiteName') else ''
                if is_case_suite_exist:
                    if not case_suite_name == CaseSuite.find_one(
                            {"_id": ObjectId(pre_import_case_info.get('caseSuiteId'))})['name']:
                        CaseSuite.update({"_id": ObjectId(pre_import_case_info.get('caseSuiteId'))},
                                                  {'$set': {'name': case_suite_name}})
                    else:
                        pass
                else:
                    insert_data = dict()
                    insert_data["name"] = case_suite_name
                    insert_data["status"] = True
                    insert_data["projectId"] = ObjectId(project_id)
                    insert_data["lastUpdateTime"] = datetime.datetime.utcnow()
                    insert_data["createAt"] = datetime.datetime.utcnow()
                    insert_data["creatorNickName"] = current_user_name
                    insert_data["lastUpdatorNickName"] = current_user_name
                    inserted_case_suite_id = CaseSuite.insert(insert_data)

                if inserted_case_suite_id:
                    pre_import_case_info.pop('_id') if is_case_exist else None
                    pre_import_case_info["projectId"] = ObjectId(project_id)
                    pre_import_case_info['caseSuiteId'] = ObjectId(inserted_case_suite_id)
                    pre_import_case_info = TestingCase.filter_field(pre_import_case_info, use_set_default=True)
                    result = TestingCase.insert(pre_import_case_info)
                    import_count += 1

                else:
                    if is_case_exist:
                        pre_import_case_info = TestingCase.filter_field(pre_import_case_info, use_set_default=False)
                        result = str(TestingCase.update({"_id": ObjectId(pre_import_case_info.get('_id'))},
                                                        {'$set': pre_import_case_info})) + ' _id: {}'\
                            .format(pre_import_case_info.get('_id'))

                        update_count += 1
                    else:
                        pre_import_case_info["projectId"] = ObjectId(project_id)
                        pre_import_case_info['caseSuiteId'] = ObjectId(pre_import_case_info.get('caseSuiteId'))
                        pre_import_case_info = TestingCase.filter_field(pre_import_case_info, use_set_default=True)
                        result = TestingCase.insert(pre_import_case_info)
                        import_count += 1

            results.append(result)
        except BaseException as e:
            return jsonify({'status': 'failed', 'data': '数据导入异常: %s' % e})

    def get_returned_data(_results, _import_count, _update_count):
        _returned_data = dict()
        _returned_data['status'] = 'ok'
        if import_count > 0 and update_count == 0:
            _returned_data['data'] = '操作成功, 共成功导入 %s 条用例' % _import_count
            # _returned_data['log'] = '导入数据_id: %s' % _results
        elif update_count > 0 and import_count == 0:
            _returned_data['data'] = '操作成功, 共成功覆盖 %s 条用例' % _update_count
            # _returned_data['log'] = '导入数据_id: %s' % _results
        elif import_count > 0 and update_count > 0:
            _returned_data['data'] = '操作成功, 共成功导入 %s 条用例、覆盖 %s 条用例' % (import_count, update_count)
            # _returned_data['log'] = '导入数据_id: %s' % _results
        else:
            _returned_data['data'] = '操作成功，但啥都没导入 / 覆盖'
            # _returned_data['log'] = None
        return jsonify(_returned_data)

    returned_data = get_returned_data(results, import_count, update_count)
    return returned_data


@app.route('/api/exportTestCases', methods=['POST'])
@login_required
def export_test_cases():
    request_data = request.get_json()

    def is_list_valid(input_data):
        is_valid = isinstance(input_data, list) and len(input_data) > 0
        return is_valid

    testing_case_ids = request_data.get('testingCaseIds') if is_list_valid(request_data.get('testingCaseIds')) else []
    case_suite_ids = request_data.get('caseSuiteIds') if is_list_valid(request_data.get('caseSuiteIds')) else []

    if not testing_case_ids and not case_suite_ids:
        return jsonify({'status': 'failed', 'data': '参数不合法!'})

    try:
        testing_case_ids = list(map(lambda x: ObjectId(x), testing_case_ids))
        case_suite_ids = list(map(lambda x: ObjectId(x), case_suite_ids))
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '参数不合法: %s' % e})

    query = {
        '$or': [
            {'_id': {'$in': testing_case_ids}, 'isDeleted': {'$ne': True}},
            {'caseSuiteId': {'$in': case_suite_ids}, 'isDeleted': {'$ne': True}}
        ]
    }

    def export_case_format(case):
        export_case = list()
        for key in test_case_map.keys():
            if isinstance(case.get(key), list):
                case_data = '；'.join(([str(x) if common.can_convert_to_str(x) else '' for x in case[key]]))
            elif isinstance(case.get(key), datetime.datetime):
                case_data = str(case.get(key)).replace('.', ':', 1) \
                    if common.can_convert_to_str(case.get(key)) \
                        and str(case.get(key)).count('.') < 2 else str(case.get(key))
            else:
                case_data = str(case.get(key)) if case.get(key) is not None else ''
            export_case.append(case_data)
        return export_case

    def add_case_suite_name(_case_info):
        _case_suite_id = _case_info.get('caseSuiteId')
        try:
            case_suite_name = CaseSuite.find_one({'_id': _case_suite_id})['name'] \
                if CaseSuite.find_one({'_id': _case_suite_id}) else ''
            _case_info['caseSuiteName'] = case_suite_name if case_suite_name else ''
        except BaseException as e:
            print(e)
        return _case_info

    export_testing_cases = map(export_case_format,  map(add_case_suite_name, TestingCase.find(query)))

    bytes_io = BytesIO()
    workbook = xlsxwriter.Workbook(bytes_io, {'in_memory': True})
    sheet = workbook.add_worksheet(u'测试用例')

    for index, value in enumerate(test_case_map.values()):
        sheet.write(0, index, value)

    for col_index, values in enumerate(export_testing_cases):
        for row_index, value in enumerate(values):
            sheet.write(col_index + 1, row_index, value)

    workbook.close()

    bytes_io.seek(0)
    return send_file(bytes_io, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')






