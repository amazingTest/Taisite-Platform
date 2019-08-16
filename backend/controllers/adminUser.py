#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from flask import Flask, jsonify, request, abort
from models.adminUser import AdminUser
from bson import ObjectId
from utils import common
import datetime
import json


@app.route('/api/adminUser', methods=['GET'])
def admin_user():
    pass





