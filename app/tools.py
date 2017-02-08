#!/usr/bin/python
# -*- coding:utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, session
from datetime import datetime, timedelta

def apply_csrf_token(expire = 3600, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    json_dict = { 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
    for key in kwargs:
        json_dict['key'] = kwargs[key]
    token = s.dumps(json_dict)
    session.setdefault('csrf_token',[]).append(token)
    return token

def check_csrf_token(token, expire = 3600, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    try:
        json_dict = s.loads(token)
        if datetime.now() - datetime.strptime(json_dict['timestamp'], '%Y-%m-%d %H:%M:%S.%f') > timedelta(seconds=expire):
            return False
        if not all([json_dict[key] == kwargs[key] for key in kwargs]):
            return False

        return True
    except:
        return False

