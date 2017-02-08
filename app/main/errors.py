#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import jsonify
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    json_str = {'status': 'fail', 'message': '404 ERROR!'}
    return jsonify(json_str), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    json_str = {'status': 'fail', 'message': '500 ERROR!'}
    return jsonify(json_str), 500
