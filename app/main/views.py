#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template, abort, flash, redirect, url_for, request, current_app, jsonify
from flask.ext.login import current_user, login_required
import json

from app.main.models.post import Post
from . import main
from .forms import check_edit_profile_admin_data, check_edit_profile_data, check_post_data
from .. import db
from ..auth.models.permission import Permission
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
            json_str = {'status': 'success', 'message': 'add post successfully!', 'result': {'post':post.to_json()}}
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

@main.route('/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    json_str = {'status': 'success', 'message': 'get user successfully', 'result': {'user': user.to_json()}}
    return jsonify(json_str)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.roles = form.roles.data
        user.permissions = form.permissions.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.roles.data = user.roles.all()
    form.permissions.data = user.permissions.all()
    form.about_me.data = user.about_me
    return render_template('main/edit_profile.html', form=form, user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('main/post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user.id != post.author_id and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('post', id=post.id))
    form.body.data = post.body
    return render_template('main/edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('main/followers.html', user=user, title="Followers of", endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followees/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followees.paginate(page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('main/followers.html', user=user, title="Followed by", endpoint='.followees', pagination=pagination, follows=follows)
