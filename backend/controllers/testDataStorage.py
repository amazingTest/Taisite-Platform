#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort, send_file
from models.testDataStorage import TestDataStorage
from bson import ObjectId
from utils import common
from flask_login import login_required
import datetime
import ast


@app.route('/api/project/<project_id>/testDataStorageList', methods=['GET', 'POST'])
@login_required
def test_data_storage_list(project_id):
    # TODO 性能优化
    total_num, storages = common.get_total_num_and_arranged_data(TestDataStorage, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': storages}})


@app.route('/api/project/<project_id>/testDataStorageList/<storage_id>', methods=['GET'])
@login_required
def storage_detail(project_id, storage_id):
    storage = TestDataStorage.find_one({'_id': ObjectId(storage_id)})
    storage = common.format_response_in_dic(storage)
    return jsonify({'status': 'ok', 'data': storage}) if storage else \
        jsonify({'status': 'failed', 'data': '未找到测试数据仓库详情'})


@app.route('/api/project/<project_id>/addTestDataStorage', methods=['POST'])
@login_required
def add_storage(project_id):
    request_data = request.get_json()
    request_data["status"] = True
    request_data["projectId"] = ObjectId(project_id)
    request_data["createAt"] = datetime.datetime.utcnow()
    request_data["lastUpdateTime"] = datetime.datetime.utcnow()
    if 'dataMap' in request_data:
        request_data['dataMap'] = ast.literal_eval(request_data['dataMap'])
        if not isinstance(request_data['dataMap'], dict):
            return jsonify({'status': 'failed', 'data': '数据字典必须为字典格式!'})
    filtered_data = TestDataStorage.filter_field(request_data, use_set_default=True)
    try:
        TestDataStorage.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '添加失败 %s' % e})


@app.route('/api/project/<project_id>/testDataStorageList/<storage_id>/updateStorage', methods=['POST'])
@login_required
def update_storage(project_id, storage_id):

    json_data = request.get_json()

    if 'dataMap' in json_data:
        json_data['dataMap'] = ast.literal_eval(json_data['dataMap'])
        if not isinstance(json_data['dataMap'], dict):
            return jsonify({'status': 'failed', 'data': '数据字典必须为字典格式!'})
    try:
        filtered_data = TestDataStorage.filter_field(json_data)
        for key, value in filtered_data.items():
            TestDataStorage.update({"_id": ObjectId(storage_id)},
                                   {'$set': {key: value}})
        update_response = TestDataStorage.update({"_id": ObjectId(storage_id)},
                           {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})