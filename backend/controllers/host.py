#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import jsonify, request
from models.host import Host
from bson import ObjectId
from utils import common
import datetime
from flask_login import login_required


@app.route('/api/project/<project_id>/hostList', methods=['GET'])
@login_required
def host_list(project_id):
    total_num, hosts = common.get_total_num_and_arranged_data(Host, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': hosts}})


@app.route('/api/project/<project_id>/addHost', methods=['POST'])
@login_required
def add_host(project_id):
    try:
        request.get_json()["status"] = True
        request.get_json()["projectId"] = ObjectId(project_id)
        request.get_json()["createAt"] = datetime.datetime.utcnow()
        request.get_json()["lastUpdateTime"] = datetime.datetime.utcnow()
        filtered_data = Host.filter_field(request.get_json(), use_set_default=True)
        Host.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/hostList/<host_id>/updateHost', methods=['POST'])
@login_required
def update_host(project_id, host_id):
    try:
        filtered_data = Host.filter_field(request.get_json())
        for key, value in filtered_data.items():
            Host.update({"_id": ObjectId(host_id)},
                        {'$set': {key: value}})
        update_response = Host.update({"_id": ObjectId(host_id)},
                    {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


