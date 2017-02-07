#!/usr/bin/python
# -*- coding:utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, session
from datetime import datetime, timedelta

def apply_csrf_token(expire = 3600):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    token = s.dumps({ 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})
    session.setdefault('csrf_token',[]).append(token)
    return token

def check_csrf_token(token, expire = 3600):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    try:
        timestamp = s.loads(token)['timestamp']
    except:
        return False

    if datetime.now() - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f') <= timedelta(seconds=expire):
        return True
    else:
        return False