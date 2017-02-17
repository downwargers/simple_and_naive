#!/usr/bin/python
# -*- coding:utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, session
from flask.ext.login import current_user
from datetime import datetime, timedelta


def apply_token(expire=3600, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    json_dict = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'user_id': current_user.id}
    for key in kwargs:
        json_dict['key'] = kwargs[key]
    token = s.dumps(json_dict)
    session['csrf_token'] = []
    session['csrf_token'].append(token)
    return token


def check_token(token, expire=3600, **kwargs):
    print current_user, current_user.username
    if not token or token not in session.setdefault('csrf_token',[]):
        return False
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = expire)
    #try:
    json_dict = s.loads(token)
    print json_dict
    if datetime.now() - datetime.strptime(json_dict['timestamp'], '%Y-%m-%d %H:%M:%S.%f') > timedelta(seconds=expire):
        print 'AAA'
        return False
    if current_user.is_anonymous or json_dict['user_id'] != current_user.id:
        print 'BBB'
        return False
    if not all([json_dict[key] == kwargs[key] for key in kwargs]):
        print 'CCC'
        return False
    return True
    '''except:
        print 'DDD'
        return False'''

