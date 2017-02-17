#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import redirect, request, url_for, abort, jsonify, current_app
from flask.ext.login import login_user, logout_user, login_required, current_user

from .models.user import User
from .models.role import Role
from ..main.models.picture import Picture
from . import auth
from .forms import check_login_data, check_registration_data, check_edit_profile_admin_data, check_edit_profile_data
from .. import db
from ..email import send_email
from ..tools import apply_token, check_token
from ..decoraters import token_required
import json
import hashlib
import os


@auth.route('/user', methods=['GET'])
def get_user():
    user = User.query.filter_by(username=request.args.get('username')).first()
    if user is None:
        abort(404)
    if current_user.is_administrator() and request.args.get('lazy') == 'False':
        user_content = user.to_json()
    else:
        user_content = user.to_json(lazy=True)
    json_str = {'status': 'success', 'message': 'get user successfully', 'result': {'user': user_content}}
    return jsonify(json_str)


@auth.route('/user', methods=['POST'])
def register():
    request_info = json.loads(request.data)
    if check_registration_data(request_info):
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
    json_str = {'status': 'fail', 'message': 'register unseccessfully'}
    return jsonify(json_str)


@auth.route('/user', methods=['PUT'])
@login_required
@token_required
def edit_user_profile():
    request_info = json.loads(request.data)
    if current_user.is_administrator():
        user = User.query.filter_by(id=request_info['id']).first()
        if not user:
            json_str = {'status': 'fail', 'message': 'user does not exist!'}
            return jsonify(json_str)
        if check_edit_profile_admin_data(request_info, user):
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
        if check_edit_profile_data(request_info):
            current_user.username = request_info['username']
            current_user.about_me = request_info['about_me']
            db.session.add(current_user)
            db.session.commit()
            json_str = {'status': 'success', 'message': 'Your profile has been updated.'}
            return jsonify(json_str)
    json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
    return jsonify(json_str)


@auth.route('/user', methods=['DELETE'])
@login_required
@token_required
def delete_user_profile():
    request_info = json.loads(request.data)
    if current_user.is_administrator():
        user = User.query.filter_by(id=request_info['id']).first()
        if not user:
            json_str = {'status': 'fail', 'message': 'user does not exist!'}
            return jsonify(json_str)
        if check_edit_profile_admin_data(request_info, user):
            user.alive = False
            db.session.add(user)
            db.session.commit()
            logout_user()
            json_str = {'status': 'success', 'message': 'Delete the user successfully.'}
            return jsonify(json_str)
    else:
        if check_edit_profile_data(request_info):
            current_user.alive = False
            db.session.add(current_user)
            db.session.commit()
            logout_user()
            json_str = {'status': 'success', 'message': 'Delete your user successfully.'}
            return jsonify(json_str)
    json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
    return jsonify(json_str)


@auth.route('/check_email', methods=['GET'])
def check_email():
    user = User.query.filter_by(email=request.args.get('email')).first()
    print user, request.args.get('email')
    if user:
        usable = False
    else:
        usable = True
    json_str = {'status': 'success', 'message': 'check email seccessfully', 'result': {'email_usable': usable}}
    return jsonify(json_str)


@auth.route('/edit_avatar', methods=['POST'])
@login_required
def edit_profile():
    if check_token(request.form['token']):
        if current_user.is_administrator():
            request_info = json.loads(request.data)
            user = User.query.filter_by(request_info['id']).first()
            if not user:
                json_str = {'status': 'fail', 'status_code': 1, 'message': 'user doesn`t exist!'}
                return jsonify(json_str)
            image = request.files['avatar']
            avatar_name = hashlib.md5(os.urandom(21)).hexdigest()
            for size in current_app.config['AVATAR_SIZE']:
                Picture(image, name=avatar_name, type='avatar', size=size)
            user.avatar = avatar_name
            db.session.add(user)
            db.session.commit()
            json_str = {'status': 'success', 'status_code': 0, 'message': 'the avatar has been updated.'}
            return jsonify(json_str)
        image = request.files['avatar']
        avatar_name = hashlib.md5(os.urandom(21)).hexdigest()
        for size in current_app.config['AVATAR_SIZE']:
            Picture(image, name=avatar_name, type='avatar', size=size)
        current_user.avatar = avatar_name
        db.session.add(current_user)
        db.session.commit()
        json_str = {'status': 'success', 'status_code': 0, 'message': 'Your avatar has been updated.'}
        return jsonify(json_str)
    else:
        json_str = {'status': 'fail', 'status_code': 3, 'message': 'please login again'}
        return jsonify(json_str)


@auth.route('/get_avatar', methods=['GET'])
def get_avatar():
    user = User.query.filter_by(id=int(request.args.get('id'))).first()
    if not user:
        json_str = {'status': 'fail', 'message': 'user doesn`t exist!'}
        return jsonify(json_str)
    avatar_size = request.args.get('size', 'XL')
    avatar_name = (user.avatar or current_app.config['DEFAULT_AVATAR']) + '_' + avatar_size
    avatar = Picture.query.filter_by(name=avatar_name).first()
    if not avatar:
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'get avatar unsuccessfully.'}
        return jsonify(json_str)

    json_str = {'status': 'success', 'status_code': 0, 'message': 'Your avatar has been updated.', 'result': {'user_avatar': avatar.file_name}}
    return jsonify(json_str)


@auth.route('/login', methods=['POST'])
def login():
    request_info = json.loads(request.data)
    if check_login_data(request_info):
        user = User.query.filter_by(email=request_info.get('email')).first()
        if user is not None and user.verify_password(request_info.get('password')):
            login_user(user, request_info.get('remember_me', False))
            json_str = {'status': 'success', 'message': 'You have been logged in successfully!', 'result': {'user': user.to_json(), 'remember_me': request_info.get('remember_me', False)}}
            response = jsonify(json_str)
            response.set_cookie('token', apply_token())
            return response
    json_str = {'status': 'fail', 'message': 'login unseccessfully'}
    return jsonify(json_str)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    json_str = {'status': 'success', 'login_require': True, 'message': 'You have been logged out.'}
    return jsonify(json_str)


@auth.route('/confirm/<token>')
def confirm(token):
    if User.confirm(token):
        json_str = {'status': 'success', 'message': 'You have confirmed your account. Thanks!'}
        return jsonify(json_str)
    else:
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