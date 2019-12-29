#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort
from models.project import Project
from bson import ObjectId
from utils import common
from flask_login import login_required
import datetime


@app.route('/api/project/projectList', methods=['GET'])
@login_required
def project_list():
    total_num, projects = common.get_total_num_and_arranged_data(Project, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': projects}})


@app.route('/api/project/<project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    res = Project.find_one({'_id': ObjectId(project_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/project/addProject', methods=['POST'])
@login_required
def add_project():
    try:
        request.get_json()["status"] = True
        request.get_json()["createAt"] = datetime.datetime.utcnow()
        request.get_json()["lastUpdateTime"] = datetime.datetime.utcnow()
        filtered_data = Project.filter_field(request.get_json(), use_set_default=True)
        Project.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateProject', methods=['POST'])
@login_required
def update_project(project_id):
    try:
        filtered_data = Project.filter_field(request.get_json())
        for key, value in filtered_data.items():
            Project.update({"_id": ObjectId(project_id)},
                           {'$set': {key: value}})
        update_response = Project.update({"_id": ObjectId(project_id)},
                       {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}},)
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


