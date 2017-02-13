#!/usr/bin/python
# -*- coding:utf-8 -*-
from functools import wraps

from flask import abort, request, jsonify
from flask.ext.login import current_user

from app.auth.models.permission import Permission
from tools import check_token
import json


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)



def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE'] and not check_token(json.loads(request.data).get('token')):
            json_str = {'status': 'fail', 'status_code': 3, 'message': 'please login again'}
            return jsonify(json_str)
        return f(*args, **kwargs)
    return decorated_function
