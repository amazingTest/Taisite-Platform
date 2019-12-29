#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from app import cron_manager
from flask import jsonify, request
from flask_login import login_required
from utils.cron.interfaceTestCron import Cron
from models.cronTab import CronTab
from utils import common
from bson import ObjectId
import datetime


@app.route('/api/cronList', methods=['get'])
@login_required
def cron_list():
    def time_stamp2str(cron):
        if cron.get('next_run_time'):
            cron['next_run_time'] = common.time_stamp2str(cron['next_run_time'])
        return cron
    total_num, crons = common.get_total_num_and_arranged_data(CronTab, request.args)
    crons = list(map(time_stamp2str, crons))
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': crons}})


@app.route('/api/project/<project_id>/addCron', methods=['post'])
@login_required
def add_cron(project_id):
    try:
        request.get_json()["projectId"] = ObjectId(project_id)
        request.get_json()["createAt"] = datetime.datetime.utcnow()
        request.get_json()["lastUpdateTime"] = datetime.datetime.utcnow()
        data = request.get_json()

        if 'interval' in data:
            data['interval'] = float(data['interval'])

        if 'interval' in data and data['interval'] < 60:
            return jsonify({'status': 'failed', 'data': '定时任务间隔不可小于60秒！'})

        if 'runDate' in data:
            data['runDate'] = common.frontend_date_str2datetime(data['runDate'])

        filtered_data = CronTab.filter_field(data, use_set_default=True)
        if filtered_data.get('runDate'):
            cron = Cron(test_case_suite_id_list=filtered_data.get('testCaseSuiteIdList'),
                        test_domain=filtered_data.get('testDomain'),
                        alarm_mail_list=filtered_data.get('alarmMailList'),
                        is_ding_ding_notify=filtered_data.get('isDingDingNotify'),
                        ding_ding_access_token=filtered_data.get('dingdingAccessToken'),
                        ding_ding_notify_strategy=filtered_data.get('dingdingNotifyStrategy'),
                        is_enterprise_wechat_notify=filtered_data.get('isEnterpriseWechatNotify'),
                        enterprise_wechat_access_token=filtered_data.get('enterpriseWechatAccessToken'),
                        enterprise_wechat_notify_strategy=filtered_data.get('enterpriseWechatNotifyStrategy'),
                        trigger_type=filtered_data.get('triggerType'),
                        test_case_id_list=filtered_data.get('testCaseIdList'),
                        is_execute_forbiddened_case=filtered_data.get('isExecuteForbiddenedCase'),
                        run_date=filtered_data.get('runDate'))
        else:
            cron = Cron(test_case_suite_id_list=filtered_data.get('testCaseSuiteIdList'),
                        test_domain=filtered_data.get('testDomain'),
                        alarm_mail_list=filtered_data.get('alarmMailList'),
                        is_ding_ding_notify=filtered_data.get('isDingDingNotify'),
                        ding_ding_access_token=filtered_data.get('dingdingAccessToken'),
                        ding_ding_notify_strategy=filtered_data.get('dingdingNotifyStrategy'),
                        is_enterprise_wechat_notify=filtered_data.get('isEnterpriseWechatNotify'),
                        enterprise_wechat_access_token=filtered_data.get('enterpriseWechatAccessToken'),
                        enterprise_wechat_notify_strategy=filtered_data.get('enterpriseWechatNotifyStrategy'),
                        trigger_type=filtered_data.get('triggerType'),
                        test_case_id_list=filtered_data.get('testCaseIdList'),
                        is_execute_forbiddened_case=filtered_data.get('isExecuteForbiddenedCase'),
                        seconds=filtered_data.get('interval'))
        cron_id = cron_manager.add_cron(cron)
        for key, value in filtered_data.items():

            CronTab.update({"_id": cron_id},
                           {'$set': {key: value}})
        update_response = CronTab.update({"_id": cron_id},
                                         {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '新建成功但未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败: %s' % e})


@app.route('/api/cronList/<cron_id>/updateCron', methods=['post'])
@login_required
def update_cron(cron_id):
    data = request.get_json()
    if data and data.get('triggerType') == 'interval' and 'runDate' in data:
        data.pop('runDate')
    elif data and data.get('triggerType') == 'date' and 'interval' in data:
        data.pop('interval')

    if 'interval' in data:
        data['interval'] = float(data['interval'])

    if 'interval' in data and data['interval'] < 60:
        return jsonify({'status': 'failed', 'data': '定时任务间隔不可小于60秒！'})

    if 'runDate' in data:
        data['runDate'] = common.frontend_date_str2datetime(data['runDate'])

    has_next_run_time = True if 'next_run_time' in data and data.pop('next_run_time') else False  # 判断是否需要重启cron
    data = CronTab.filter_field(data)
    try:
        cron_manager.update_cron(cron_id=cron_id, cron_info=data)
        # TODO 仅修改名字/描述时，也重启了定时器，导致下一次运行时间变更, 解决成本有点大，暂不解决:)
        cron_manager.pause_cron(cron_id=cron_id)
        cron_manager.resume_cron(cron_id=cron_id) if has_next_run_time else None

        for key, value in data.items():
            CronTab.update({"_id": cron_id},
                           {'$set': {key: value}})
        update_response = CronTab.update({"_id": cron_id},
                                         {'$set': {'lastUpdateTime': datetime.datetime.utcnow()}})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})

        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


@app.route('/api/cronList/<cron_id>/pauseCron', methods=['post'])
@login_required
def pause_cron(cron_id):
    try:
        cron_manager.pause_cron(cron_id=cron_id)
        CronTab.update({"_id": cron_id},
                       {'$set': {'status': 'PAUSED'}})
        return jsonify({'status': 'ok', 'data': '停用成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '停用失败: %s' % e})


@app.route('/api/cronList/<cron_id>/resumeCron', methods=['post'])
@login_required
def resume_cron(cron_id):
    try:
        cron_manager.resume_cron(cron_id=cron_id)
        CronTab.update({"_id": cron_id},
                               {'$set': {'status': 'RESUMED'}})
        return jsonify({'status': 'ok', 'data': '启动成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '启动失败: %s' % e})


@app.route('/api/cronList/<cron_id>/delCron', methods=['post'])
@login_required
def del_cron(cron_id):
    try:
        cron_manager.del_cron(cron_id=cron_id)
        return jsonify({'status': 'ok', 'data': '删除成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '删除失败: %s' % e})


@app.route('/api/cronList/start', methods=['post'])
@login_required
def start():
    try:
        data = request.get_json()
        if data:
            paused = data.get('paused')
        else:
            paused = None
        cron_manager.start(paused=paused)
        return jsonify({'status': 'ok', 'data': '调度器启动成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '调度器启动失败: %s' % e})


@app.route('/api/cronList/shutdown', methods=['post'])
@login_required
def shutdown():
    try:
        data = request.get_json()
        force_shutdown = data.get('forceShutdown')
        cron_manager.shutdown(force_shutdown=force_shutdown)
        return jsonify({'status': 'ok', 'data': '调度器关闭成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '调度器关闭失败: %s' % e})






