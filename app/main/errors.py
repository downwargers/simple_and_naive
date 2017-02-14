#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import jsonify
from . import main


@main.errorhandler(404)
def page_not_found(e):
    json_str = {'status': 'fail', 'status_code': 404, 'message': '404 ERROR!'}
    return jsonify(json_str), 404


@main.errorhandler(500)
def internal_server_error(e):
    json_str = {'status': 'fail', 'status_code': 500, 'message': '500 ERROR!'}
    return jsonify(json_str), 500
