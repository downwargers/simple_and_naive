#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import redirect, request, url_for, flash, abort, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user

from .models.user import User
from .models.role import Role
from . import auth
from .forms import check_login_data, check_registration_data, check_edit_profile_admin_data, check_edit_profile_data
from .. import db
from ..email import send_email
from ..tools import apply_token, check_token
import json


@auth.route('/user', methods=['GET'])
def get_user():
    user = User.query.filter_by(username=request.args.get('username')).first()
    if user is None:
        abort(404)
    json_str = {'status': 'success', 'message': 'get user successfully', 'result': {'user': user.to_json()}}
    return jsonify(json_str)


@auth.route('/user', methods=['POST'])
def register():
    request_info = json.loads(request.data)
    if check_token(request_info.get('token'), id=current_user.id) and check_registration_data(request_info):
        user = User.query.filter_by(email=request_info.get('email')).first()
        if user is not None and user.verify_password(request_info.get('password')):
            user = User(email=request_info.get('email'), username=request_info.get('username'), password=request_info.get('password'))
            db.session.add(user)
            db.session.commit()
            user.roles = Role.query.filter(Role.default is True)
            db.session.commit()
            login_user(user, request_info.get('remember_me', False))
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
            json_str = {'status': 'success', 'message': 'register successfully!'}
            return jsonify(json_str)
    abort(500)


@auth.route('/user/', methods=['PUT'])
@login_required
def edit_user_profile():
    request_info = json.loads(request.data)
    if current_user.is_administrator():
        user = User.query.filter_by(id=request_info['id']).first()
        if not user:
            json_str = {'status': 'fail', 'message': 'user does not exist!'}
            return jsonify(json_str)
        if check_token(request_info.get('token'), id=id) and check_edit_profile_admin_data(request_info, user):
            user.email = request_info['email']
            user.username = request_info['username']
            user.confirmed = request_info['confirmed']
            user.set_roles(request_info['roles'])
            user.set_permissions(request_info['permissions'])
            user.about_me = request_info['about_me']
            db.session.add(user)
            db.session.commit()
            json_str = {'status': 'success', 'message': 'The profile has been updated.'}
            return jsonify(json_str)
    else:
        if check_token(request_info.get('token')) and check_edit_profile_data(request_info):
            current_user.username = request_info['username']
            current_user.about_me = request_info['about_me']
            db.session.add(current_user)
            db.session.commit()
            json_str = {'status': 'success', 'message': 'Your profile has been updated.'}
            return jsonify(json_str)
    json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
    return jsonify(json_str)


@auth.route('/user/', methods=['DELETE'])
@login_required
def edit_user_profile():
    request_info = json.loads(request.data)
    if current_user.is_administrator():
        user = User.query.filter_by(id=request_info['id']).first()
        if not user:
            json_str = {'status': 'fail', 'message': 'user does not exist!'}
            return jsonify(json_str)
        if check_token(request_info.get('token'), id=id) and check_edit_profile_admin_data(request_info, user):
            user.alive = False
            db.session.add(user)
            db.session.commit()
            logout_user()
            json_str = {'status': 'success', 'message': 'Delete the user successfully.'}
            return jsonify(json_str)
    else:
        if check_token(request_info.get('token')) and check_edit_profile_data(request_info):
            current_user.alive = False
            db.session.add(current_user)
            db.session.commit()
            logout_user()
            json_str = {'status': 'success', 'message': 'Delete your user successfully.'}
            return jsonify(json_str)
    json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
    return jsonify(json_str)


@auth.route('/login', methods=['POST'])
def login():
    request_info = json.loads(request.data)
    if check_login_data(request_info):
        user = User.query.filter_by(email=request_info.get('email')).first()
        if user is not None and user.verify_password(request_info.get('password')):
            login_user(user, request_info.get('remember_me', False))
            json_str = {'status': 'success', 'message': 'You have been logged in successfully!', 'result': {'user': user.to_json(), 'remember_me': request_info.get('remember_me', False)}}
            return jsonify(json_str)
    json_str = {'status': 'fail', 'message': 'login unseccessfully'}
    response = jsonify(json_str)
    response.set_cookie('token', apply_token())
    return response


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    json_str = {'status': 'success', 'login_require': True, 'message': 'You have been logged out.'}
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