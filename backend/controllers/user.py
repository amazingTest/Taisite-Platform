#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import jsonify, request, render_template, make_response, abort
from models.adminUser import AdminUser
from flask_login import UserMixin, login_user, logout_user
from app import login_manager
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


class User(UserMixin):

    @staticmethod
    def query_user(user_name):
        try:
            user = AdminUser.find_one({'username': user_name, 'isDeleted': {"$ne": True}})
            return user
        except BaseException:
            pass

    @staticmethod
    def get_nick_name(user_name):
        try:
            user = AdminUser.find_one({'username': user_name, 'isDeleted': {"$ne": True}})
            nick_name = user['nickName'] if user else '未知用户'
            return nick_name
        except BaseException:
            return '未知用户'


class SecretUser(User):

    def __init__(self, username=None, password=None):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    if User.query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id
        return curr_user


@login_manager.unauthorized_handler
def unauthorized_handler():
    abort(401)


@app.route('/api/login', methods=['POST'])
def log_in():
    request_data = request.get_json()
    user_name = request_data.get('username') if request_data else None
    pass_word = request_data.get('password') if request_data else None
    user = User.query_user(user_name)
    if user is not None and user['password'] == pass_word:
        curr_user = User()
        curr_user.id = user_name
        login_user(curr_user, remember=True)
        nick_name = User.get_nick_name(user_name)
        res = make_response(jsonify({'status': 'ok', 'data': {'nickName': nick_name}}))
        return res
    return jsonify({'status': 'failed', 'data': '用户名 / 密码错误！'})


@app.route('/api/logout', methods=['POST', 'GET'])
def log_out():
    try:
        logout_user()
        res = make_response(jsonify({'status': 'ok', 'data': '退出登录成功'}))
        return res
    except BaseException:
        return jsonify({'status': 'failed', 'data': '退出登录失败!'})




