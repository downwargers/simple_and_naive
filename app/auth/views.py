#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, session, abort, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user

from .models.user import User
from .models.role import Role
from . import auth
from .forms import check_login_data, check_registration_data
from .. import db
from ..email import send_email
from ..tools import apply_csrf_token, check_csrf_token
import json


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if check_csrf_token(request_info.get('csrf_token')) and check_login_data(request_info):
            user = User.query.filter_by(email=request_info.get('email')).first()
            if user is not None and user.verify_password(request_info.get('password')):
                login_user(user, request_info.get('remember_me', False))
                json_str = {'status': 'success', 'message': 'You have been logged in successfully!', 'result': {'user':user.to_json(), 'remember_me': request_info.get('remember_me', False)}}
                return jsonify(json_str)
        json_str = {'status': 'fail', 'message': 'login unseccessfully'}
        return jsonify(json_str)
    else:
        csrf_token = apply_csrf_token()
        json_str = {'status': 'success', 'login_require': True, 'message': 'login please', 'result': {'csrf_token': csrf_token}}
        return jsonify(json_str)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    json_str = {'status': 'success', 'login_require': True, 'message': 'You have been logged out.'}
    return jsonify(json_str)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if check_csrf_token(request_info.get('csrf_token')) and check_registration_data(request_info):
            user = User.query.filter_by(email=request_info.get('email')).first()
            if user is not None and user.verify_password(request_info.get('password')):
                user = User(email=request_info.get('email'), username=request_info.get('username'), password=request_info.get('password'))
                db.session.add(user)
                db.session.commit()
                user.roles = Role.query.filter(Role.default is True)
                db.session.commit()
                token = user.generate_confirmation_token()
                send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
                json_str = {'status': 'success', 'message': 'register successfully!', 'result': {'user':user.to_json()}}
                return jsonify(json_str)
        abort(500)
    else:
        csrf_token = apply_csrf_token()
        json_str = {'status': 'success', 'message': 'register please', 'result': {'csrf_token': csrf_token}}
        return jsonify(json_str)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed or current_user.confirm(token):
        json_str = {'status': 'success', 'message': 'You have confirmed your account. Thanks!'}
        return jsonify(json_str)
    else:
        flash('The confirmation link is invalid or has expired.')
        json_str = {'status': 'fail', 'message': 'The confirmation link is invalid or has expired.'}
        return jsonify(json_str)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    json_str = {'status': 'seccess', 'message': 'A new confirmation email has been sent to you by email.'}
    return jsonify(json_str)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        json_str = {'status': 'seccess', 'message': 'A new confirmation email has been sent to you by email.'}
    else:
        json_str = {'status': 'fail', 'message': 'Your account need to be confirmed.'}
    return jsonify(json_str)