#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import abort, request, current_app, jsonify
from flask.ext.login import current_user, login_required
import json

from .models.post import Post
from .models.picture import Picture
from . import main
from .forms import check_edit_profile_admin_data, check_edit_profile_data, check_post_data
from .. import db
from ..auth.models.permission import Permission
from ..auth.models.role import Role
from ..auth.models.user import User
from ..decoraters import admin_required, permission_required
from ..tools import apply_csrf_token, check_csrf_token


@main.route('/posts', methods=['GET'])
def get_post():
    get_type = request.args.get('type')
    if get_type == 'all':
        query = Post.query.filter_by(alive=True)
    elif get_type == 'person':
        user = User.query.filter_by(username=request.args.get('username')).first()
        if user is None:
            abort(404)
        query = Post.query.filter_by(alive=True).filter(Post.author_id == user.id)
    elif get_type == 'timeline':
        user = User.query.filter_by(username=request.args.get('username')).first()
        if user is None:
            abort(404)
        query = Post.query.filter_by(alive=True).filter(Post.author_id.in_([followee.id for followee in user.follewees.all()]))
    else:
        json_str = {'status': 'fail', 'message': 'unknown type'}
        return jsonify(json_str)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    posts = [post.to_json() for post in posts]
    json_str = {'status': 'success', 'message': 'get post success', 'result': {'posts': posts}}
    return jsonify(json_str)


@main.route('/post', methods=['POST', 'GET'])
@login_required
def edit_post():
    if request.method in ['POST', 'PUT']:
        request_info = json.loads(request.data)
        if check_csrf_token(request_info.get('csrf_token')) and check_post_data(request_info):
            if request.method == 'POST':
                post = Post(body=request_info.get('body'), author=current_user._get_current_object())
            else:
                post = Post.query.filter_by(id=request_info.get('id')).first()
                post.body = request_info.get('body')
            db.session.add(post)
            db.commit()
            json_str = {'status': 'success', 'message': 'add post successfully!', 'result': {'post': post.to_json()}}
            return jsonify(json_str)
        json_str = {'status': 'fail', 'message': 'add post unseccessfully'}
        return jsonify(json_str)
    elif request.method == 'DELETE':
        request_info = json.loads(request.data)
        post = Post.query.filter_by(id=request_info.get('id')).first()
        post.alive = False
        db.session.add(post)
        db.commit()
        json_str = {'status': 'success', 'message': 'delete post successfully!', 'result': {'post': post.to_json()}}
        return jsonify(json_str)
    else:
        post = Post.query.filter_by(id=request.args.get('id')).first()
        if post:
            post_content = post.to_json()
        else:
            post_content = None
        csrf_token = apply_csrf_token()
        json_str = {'status': 'success', 'message': 'add or change post please', 'result': {'post': post_content, 'csrf_token': csrf_token}}
        return jsonify(json_str)


@main.route('/user')
def get_user():
    user = User.query.filter_by(username=request.args.get('username')).first()
    if user is None:
        abort(404)
    json_str = {'status': 'success', 'message': 'get user successfully', 'result': {'user': user.to_json()}}
    return jsonify(json_str)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        json_str = {'status': 'fail', 'message': 'user doesn`t exist!'}
        return jsonify(json_str)
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if check_csrf_token(request_info.get('csrf_token'), id=id) and check_edit_profile_admin_data(request_info, user):
            user.email = request_info['email']
            user.username = request_info['username']
            user.confirmed = request_info['confirmed']
            user.set_roles(request_info['roles'])
            user.set_permissions(request_info['permissions'])
            user.about_me = request_info['about_me']
            db.session.add(user)
            db.session.commit()
            json_str = {'status': 'success', 'message': 'The profile has been updated.', 'result': {'user': user.to_json()}}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
            return jsonify(json_str)
    else:
        csrf_token = apply_csrf_token(id=id)
        roles = [{'id': role.id, 'name':role.name} for role in Role.query.all()]
        permissions = [{'id': permission.id, 'name': permission.name} for permission in Permission.query.all()]
        json_str = {'status': 'success', 'message': 'edit user profile please', 'result': {'user': user.to_json(), 'roles': roles, 'permissions': permissions, 'csrf_token': csrf_token}}
        return jsonify(json_str)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if check_csrf_token(request_info.get('csrf_token')) and check_edit_profile_data(request_info):
            current_user.username = request_info['username']
            current_user.about_me = request_info['about_me']
            db.session.add(current_user)
            db.session.commit()
            json_str = {'status': 'success', 'message': 'Your profile has been updated.', 'result': {'user': current_user.to_json()}}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'message': 'edit profile unseccessfully'}
            return jsonify(json_str)
    else:
        csrf_token = apply_csrf_token()
        json_str = {'status': 'success', 'message': 'edit user profile please', 'result': {'user': current_user.to_json(), 'csrf_token': csrf_token}}
        return jsonify(json_str)    

@main.route('/edit-avatar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        json_str = {'status': 'fail', 'message': 'user doesn`t exist!'}
        return jsonify(json_str)
    if request.method == 'POST':
        if check_csrf_token(request.form['csrf_token']):
            image = request.files['avatar']
            user.set_avatar(image)
            json_str = {'status': 'success', 'message': 'the avatar has been updated.'}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'message': 'edit avatar unseccessfully'}
            return jsonify(json_str)
    else:
        csrf_token = apply_csrf_token(id=id)
        json_str = {'status': 'success', 'message': 'edit user avatar please', 'result': {'csrf_token': csrf_token}}
        return jsonify(json_str)


@main.route('/edit-avatar', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if check_csrf_token(request.form['csrf_token']):
            image = request.files['avatar']
            current_user.set_avatar(image)
            json_str = {'status': 'success', 'message': 'Your avatar has been updated.'}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'message': 'edit avatar unseccessfully'}
            return jsonify(json_str)
    else:
        csrf_token = apply_csrf_token()
        json_str = {'status': 'success', 'message': 'edit user profile please', 'result': {'csrf_token': csrf_token}}
        return jsonify(json_str)


@main.route('/get-avatar/<int:id>', methods=['GET'])
def get_avatar(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        json_str = {'status': 'fail', 'message': 'user doesn`t exist!'}
        return jsonify(json_str)
    avatar_size = request.args.get('size', 'XL')
    avatar_name = (user.avatar or current_app.config['DEFAULT_AVATAR']) + '_' + avatar_size
    avatar = Picture.query.filter_by(name=avatar_name).first()
    if not avatar:
        json_str = {'status': 'fail', 'message': 'get avatar unsuccessfully.'}
        return jsonify(json_str)

    json_str = {'status': 'success', 'message': 'Your avatar has been updated.', 'result': {'user_avatar': avatar.file_name}}
    return jsonify(json_str)


@main.route('/follow', methods=['POST'])
@login_required
@permission_required(Permission.FOLLOW)
def follow():
    request_info = json.loads(request.data)
    user = User.query.filter_by(id=request_info.get['id']).first()
    if user is None:
        json_str = {'status': 'fail', 'message': 'Invalid user'}
        return jsonify(json_str)
    if current_user.is_following(user):
        json_str = {'status': 'fail', 'message': 'You are already following this user.'}
        return jsonify(json_str)
    current_user.follow(user)
    json_str = {'status': 'success', 'message': 'You are now following %s.' % user.username}
    return jsonify(json_str)


@main.route('/unfollow', methods=['POST'])
@login_required
@permission_required(Permission.FOLLOW)
def unfollow():
    request_info = json.loads(request.data)
    user = User.query.filter_by(id=request_info.get['id']).first()
    if user is None:
        json_str = {'status': 'fail', 'message': 'Invalid user'}
        return jsonify(json_str)
    if not current_user.is_following(user):
        json_str = {'status': 'fail', 'message': 'You haven`t followed this user.'}
        return jsonify(json_str)
    current_user.unfollow(user)
    json_str = {'status': 'success', 'message': 'You don`t following %s any longer.' % user.username}
    return jsonify(json_str)

@main.route('/followees', methods=['GET'])
def get_followees():
    user = User.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is None:
        json_str = {'status': 'fail', 'message': 'Invalid user'}
        return jsonify(json_str)
    page = request.args.get('page', 1, type=int)
    pagination = user.followees.paginate(page, per_page=current_app.config['followees_PER_PAGE'], error_out=False)
    followees = [{'user': user.to_json(), 'timestamp': item.timestamp} for item in pagination.items]
    json_str = {'status': 'success', 'message': 'get followees successfully', 'result': {'followees': followees}}
    return jsonify(json_str)


@main.route('/followees', methods=['GET'])
def get_followees():
    user = User.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is None:
        json_str = {'status': 'fail', 'message': 'Invalid user'}
        return jsonify(json_str)
    page = request.args.get('page', 1, type=int)
    pagination = user.followees.paginate(page, per_page=current_app.config['followees_PER_PAGE'], error_out=False)
    followees = [{'user': user.to_json(), 'timestamp': item.timestamp} for item in pagination.items]
    json_str = {'status': 'success', 'message': 'get followees successfully', 'result': {'followees': followees}}
    return jsonify(json_str)
