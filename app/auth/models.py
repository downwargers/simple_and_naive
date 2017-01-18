#!/usr/bin/python
# -*- coding:utf-8 -*-
from .. import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from ..tools import ManyToMany


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    roles = ManyToMany(db, Role, UserRoleRelation, 'user_id', 'role_id')
    permissions = ManyToMany(db, Permission, UserPermissionRelation, 'user_id', 'permission_id')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        self.posts.append()

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
        permission_id = Permission.query.filter(Permission.name == permission_name).first().id
        return permission_id in [permission.id for permission in self.permissions.all()] or any([role.can(permission_id) for role in self.roles.all()])

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)

    permissions = ManyToMany(db, Permission, RolePermissionRelation, 'role_id', 'permission_id')

    def can(self, permission_name):
        if isinstance(permission_name, list):
            return all([self.can(p) for p in permission_name])
        permission_id = Permission.query.filter(Permission.name == permission_name).first().id
        return permission_id in [permission.id for permission in self.permissions.all()]

    @staticmethod
    def insert_roles():
        roles = {
            'User': ([Permission.FOLLOW, Permission.COMMENT, Permission.WRITE_ARTICLES], True),
            'Moderator': ([Permission.FOLLOW, Permission.COMMENT, Permission.WRITE_ARTICLES, Permission.MODERATE_COMMENTS], False),
            'Administrator': (Permission.ADMINISTER, False)
        }

        for r in roles:
            role = Role.query.filter(Role.name == r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][1]
            db.session.add(role)
            db.session.commit()
            permissions = roles[r][0]
            permissions_id = [permission.id for permission in Permission.query.filter(Permission.name.in_(permissions)).all()]
            role.permissions = permissions_id
            db.session.commit()


class Permission(db.Model):
    __tablename__ = 'permissions'
    FOLLOW = "FOLLOW"
    COMMENT = "COMMENT"
    WRITE_ARTICLES = "WRITE_ARTICLES"
    MODERATE_COMMENTS = "MODERATE_COMMENTS"
    ADMINISTER = "ADMINISTER"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    @staticmethod
    def insert_permissions():
        permissions = [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE_ARTICLES, Permission.MODERATE_COMMENTS, Permission.ADMINISTER]
        for p in permissions:
            permission = Permission.query.filter(Role.name == p).first()
            if permission is None:
                permission = Permission(name=p)
            db.session.add(permission)
            db.session.commit()


class UserRoleRelation(db.Model):
    __tablename__ = 'user_role_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id


class UserPermissionRelation(db.Model):
    __tablename__ = 'user_permission_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    permission_id = db.Column(db.Integer)

    def __init__(self, user_id, permission_id):
        self.user_id = user_id
        self.role_id = permission_id


class RolePermissionRelation(db.Model):
    __tablename__ = 'role_permission_relation'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer)
    permission_id = db.Column(db.Integer)

    def __init__(self, role_id, permission_id):
        self.role_id = role_id
        self.permission_id = permission_id
