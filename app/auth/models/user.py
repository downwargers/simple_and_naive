#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from ...main.models.post import Post
from ...main.models.picture import Picture
from .role import Role
from .permission import Permission
from .relations import FollowRelation
import random
import string


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    avatar = db.Column(db.String(64), null=True)
    username = db.Column(db.String(64), unique=True, index=True)
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    roles = db.relationship('Role', secondary='user_role_relation', backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def set_roles(self, role_names):
        if not isinstance(role_names, list):
            role_names = [role_names]
        roles = {role.name: role for role in Role.query.all()}
        self.clear_roles()
        for role_name in role_names:
            if isinstance(role_name, Role):
                role = role_name
            else:
                role = roles.get(role_name)
            if role:
                self.roles.append(role)
        db.session.add(self)

    def clear_roles(self):
        self.roles.delete()
        db.session.add(self)

    permissions = db.relationship('Permission', secondary='user_permission_relation', backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def set_permissions(self, permission_names):
        if not isinstance(permission_names, list):
            permission_names = [permission_names]
        permissions = {permission.name: permission for permission in Permission.query.all()}
        self.clear_permissions()
        for permission_name in permission_names:
            if isinstance(permission_name, Permission):
                permission = permission_name
            else:
                permission = permissions.get(permission_name)
            if permission:
                self.permissions.append(permission)
        db.session.add(self)

    def clear_permissions(self):
        self.permissions.delete()
        db.session.add(self)

    followers = db.relationship('FollowRelation', foreign_keys=[FollowRelation.followee_id], backref=db.backref('followee', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followees = db.relationship('FollowRelation', foreign_keys=[FollowRelation.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    def follow(self, user):
        if not self.is_following(user):
            f = FollowRelation(follower=self, followee=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followees.filter(FollowRelation.follower_id == user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followees.filter(FollowRelation.follower_id == user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter(FollowRelation.followee_id == user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(FollowRelation, FollowRelation.followee_id == Post.author_id).filter(FollowRelation.follower_id == self.id)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permission_name):
        if isinstance(permission_name, list):
            return all([self.can(p) for p in permission_name])
        a = permission_name in [permission.name for permission in self.permissions.all()] or any([permission.can(permission_name) for role in self.roles.all()])
        return a

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def set_avatar(self, f):
        avatar_name = ''.join(random.sample(string.ascii_letters + string.digits + '!@#$%^&*()_+=-', 32))
        for size in current_app.config['AVATAR_SIZE']:
            Picture(f, name=avatar_name, type='avatar', size=size)
        self.avatar = avatar_name
        db.session.add(self)
        db.commit()

    def to_json(self):
        json_dict = {}
        json_dict['id'] = self.id
        json_dict['username'] = self.username
        json_dict['email'] = self.email
        json_dict['about_me'] = self.about_me
        json_dict['last_seen'] = self.last_seen
        json_dict['confirmed'] = self.confirmed
        json_dict['roles'] = [role.name for role in self.roles.all()]
        json_dict['permissions'] = [permission.name for permission in self.permissions.all()]
        return json_dict


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
