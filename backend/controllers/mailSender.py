#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import jsonify, request
from models.mailSender import MailSender
from bson import ObjectId
from utils import common
from utils.sendReportEmail import send_report_email
import datetime
from flask_login import login_required


@app.route('/api/project/<project_id>/mailSenderList', methods=['GET'])
@login_required
def mail_sender_list(project_id):
    total_num, mail_senders = common.get_total_num_and_arranged_data(MailSender, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mail_senders}})


@app.route('/api/project/<project_id>/addMailSender', methods=['POST'])
@login_required
def add_mail_sender(project_id):
    try:
        request.get_json()["status"] = True
        request.get_json()["projectId"] = ObjectId(project_id)
        request.get_json()["createAt"] = datetime.datetime.utcnow()
        request.get_json()["lastUpdateTime"] = datetime.datetime.utcnow()
        filtered_data = MailSender.filter_field(request.get_json(), use_set_default=True)
        MailSender.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/mailSenderList/<sender_id>/updateMailSender', methods=['POST'])
@login_required
def update_mail_sender(project_id, host_id):
    try:
        filtered_data = MailSender.filter_field(request.get_json())
        for key, value in filtered_data.items():
            MailSender.update({"_id": ObjectId(host_id)},
                        {'$set': {key: value}})
        update_response = MailSender.update({"_id": ObjectId(host_id)},
                    {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


@app.route('/api/testEmailSender', methods=['POST'])
@login_required
def test_email_sender():
    request_data = request.get_json()
    user_name = request_data.get('username')
    pass_word = request_data.get('password')
    if send_report_email(user_name, pass_word, [user_name], '发件人测试', '发件人测试'):
        return jsonify({'status': 'ok', 'data': '验证通过 (*^▽^*) 您可以放心「提交」了'})
    else:
        return jsonify({'status': 'failed', 'data': '验证失败 o(╥﹏╥)o'})

