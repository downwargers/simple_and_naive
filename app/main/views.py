#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import abort, request, current_app, jsonify
from flask.ext.login import current_user, login_required
import json

from .models.post import Post
from .models.comment import Comment
from . import main
from .forms import check_post_data, check_comment_data
from .. import db
from ..auth.models.permission import Permission
from ..auth.models.user import User
from ..decoraters import permission_required, token_required


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
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'unknown type'}
        return jsonify(json_str)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    posts = [post.to_json() for post in posts]
    json_str = {'status': 'success', 'status_code': 0, 'message': 'get post success', 'result': {'posts': posts, 'page': pagination.page, 'pages': pagination.pages, 'per_page': current_app.config['POSTS_PER_PAGE']}}
    return jsonify(json_str)


@main.route('/post', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@token_required
def edit_post():
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if  check_post_data(request_info):
            post = Post(body=request_info.get('body'), author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
            json_str = {'status': 'success', 'status_code': 0, 'message': 'add post successfully!'}
            return jsonify(json_str)
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'add post unseccessfully'}
        return jsonify(json_str)
    elif request.method == 'PUT':
        request_info = json.loads(request.data)
        if check_post_data(request_info):
            post = Post.query.filter_by(id=request_info.get('id')).first()
            if post.alive is True and post.author_id == current_user.id or current_user.is_administrator():
                post.body = request_info.get('body')
                db.session.add(post)
                db.session.commit()
                json_str = {'status': 'success', 'status_code': 0, 'message': 'edit post successfully!'}
                return jsonify(json_str)
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'edit post unseccessfully'}
        return jsonify(json_str)
    elif request.method == 'DELETE':
        request_info = json.loads(request.data)
        post = Post.query.filter_by(id=request_info.get('id')).first()
        post.alive = False
        db.session.add(post)
        db.session.commit()
        json_str = {'status': 'success', 'status_code': 0, 'message': 'delete post successfully!'}
        return jsonify(json_str)
    else:
        post = Post.query.filter_by(id=int(request.args.get('id'))).first()
        if post.alive is False and not current_user.is_administrator():
            json_str = {'status': 'fail', 'status_code': 2, 'message': 'post has been deleted'}
            return jsonify(json_str)
        if post:
            post_content = post.to_json(with_author=True, with_comment=True, comment_page=int(request.args.get('page', 1)))
            json_str = {'status': 'success', 'status_code': 0, 'message': 'get post successfully!', 'result': {'post': post_content}}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'status_code': 1, 'message': 'post does not exist'}
            return jsonify(json_str)


@main.route('/comment', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@token_required
def edit_comment():
    if request.method == 'POST':
        request_info = json.loads(request.data)
        if check_comment_data(request_info):
            post = Post.query.filter_by(id=int(request_info.get('post_id'))).first()
            comment = Comment(body=request_info.get('body'), author=current_user._get_current_object(), post=post)
            db.session.add(comment)
            db.session.commit()
            json_str = {'status': 'success', 'status_code': 0, 'message': 'add comment successfully!'}
            return jsonify(json_str)
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'add comment unseccessfully'}
        return jsonify(json_str)
    elif request.method == 'PUT':
        request_info = json.loads(request.data)
        if check_comment_data(request_info):
            comment = Comment.query.filter_by(id=request_info.get('id')).first()
            if comment.alive is True and comment.author_id == current_user.id or current_user.is_administrator():
                comment.body = request_info.get('body')
                db.session.add(comment)
                db.session.commit()
                json_str = {'status': 'success', 'status_code': 0, 'message': 'edit comment successfully!'}
                return jsonify(json_str)
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'edit comment unseccessfully'}
        return jsonify(json_str)
    elif request.method == 'DELETE':
        request_info = json.loads(request.data)
        comment = Comment.query.filter_by(id=request_info.get('id')).first()
        comment.alive = False
        db.session.add(comment)
        db.session.commit()
        json_str = {'status': 'success', 'status_code': 0, 'message': 'delete comment successfully!'}
        return jsonify(json_str)
    else:
        comment = Comment.query.filter_by(id=int(request.args.get('id'))).first()
        if comment.alive is False and not current_user.is_administrator():
            json_str = {'status': 'fail', 'status_code': 2, 'message': 'comment has been deleted'}
            return jsonify(json_str)
        if comment:
            comment_content = comment.to_json(with_author=True, cascading=True, comment_page=int(request.args.get('page', 1)))
            json_str = {'status': 'success', 'status_code': 0, 'message': 'add or change comment please', 'result': {'comment': comment_content}}
            return jsonify(json_str)
        else:
            json_str = {'status': 'fail', 'status_code': 1, 'message': 'comment does not exist'}
            return jsonify(json_str)


@main.route('/follow', methods=['POST'])
@login_required
@token_required
@permission_required(Permission.FOLLOW)
def follow():
    request_info = json.loads(request.data)
    user = User.query.filter_by(id=request_info.get('id')).first()
    if user is None:
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'Invalid user'}
        return jsonify(json_str)
    if current_user.is_following(user):
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'You are already following this user.'}
        return jsonify(json_str)
    current_user.follow(user)
    json_str = {'status': 'success', 'status_code': 0, 'message': 'You are now following %s.' % user.username}
    return jsonify(json_str)


@main.route('/unfollow', methods=['POST'])
@login_required
@token_required
@permission_required(Permission.FOLLOW)
def unfollow():
    request_info = json.loads(request.data)
    user = User.query.filter_by(id=request_info.get('id')).first()
    if user is None:
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'Invalid user'}
        return jsonify(json_str)
    if not current_user.is_following(user):
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'You haven`t followed this user.'}
        return jsonify(json_str)
    current_user.unfollow(user)
    json_str = {'status': 'success', 'status_code': 0, 'message': 'You don`t following %s any longer.' % user.username}
    return jsonify(json_str)


@main.route('/followees', methods=['GET'])
def get_followees():
    user = User.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is None:
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'Invalid user'}
        return jsonify(json_str)
    page = request.args.get('page', 1, type=int)
    pagination = user.followees.paginate(page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    followees = [{'user': user.to_json(), 'timestamp': item.timestamp} for item in pagination.items]
    json_str = {'status': 'success', 'status_code': 0, 'message': 'get followees successfully', 'result': {'followees': followees}}
    return jsonify(json_str)


@main.route('/followers', methods=['GET'])
def get_followers():
    user = User.query.filter_by(id=request.args.get('id', type=int)).first()
    if user is None:
        json_str = {'status': 'fail', 'status_code': 1, 'message': 'Invalid user'}
        return jsonify(json_str)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    followers = [{'user': user.to_json(), 'timestamp': item.timestamp} for item in pagination.items]
    json_str = {'status': 'success', 'status_code': 0, 'message': 'get followers successfully', 'result': {'followers': followers}}
    return jsonify(json_str)
