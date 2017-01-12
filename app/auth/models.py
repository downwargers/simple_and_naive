#!/usr/bin/python
# -*- coding:utf-8 -*-
from .. import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


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
    permissions = db.Column(db.Integer, default=0)

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
        return True

    def show_roles_id(self):
        return [relation.role_id for relation in UserRoleRelation.query.filter(UserRoleRelation.user_id == self.id).all()]

    def set_roles(self, roles_id):
        UserRoleRelation.query.filter(UserRoleRelation.user_id == self.id).delete()
        relation_to_add = [UserRoleRelation(user_id=self.id, role_id=role_id) for role_id in roles_id]
        db.session.add_all(relation_to_add)

    def add_permissions(self, permissions):
        for permission in permissions:
            if permission != Permission.ADMINISTER:
                self.permissions |= permission

    def del_permissions(self, permissions):
        for permission in permissions:
            if permission != Permission.ADMINISTER and self.permissions | permission == self.permissions:
                self.permissions ^= permission

    def can(self, permissions):
        role_permissions = reduce(lambda x, y:x.permissions|y.permissions, UserRoleRelation.query.filter(UserRoleRelation.user_id == self.id).all())
        return self.role is not None and ((role_permissions | self.permissions) & permissions) == permissions

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
    permissions = db.Column(db.Integer)

    def add_permissions(self, permissions):
        for permission in permissions:
            if permission != Permission.ADMINISTER:
                self.permissions |= permission

    def del_permissions(self, permissions):
        for permission in permissions:
            if permission != Permission.ADMINISTER and self.permissions | permission == self.permissions:
                self.permissions ^= permission

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (Permission.ADMINISTER, False)
        }

        for r in roles:
            role = Role.query.filter(Role.name == r).first()
        if role is None:
            role = Role(name=r)
        role.permissions = roles[r][0]
        role.default = roles[r][1]
        db.session.add(role)
        db.session.commit()


class UserRoleRelation(db.Model):
    __tablename__ = 'user_role_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def __init__(self, user, role):
        self.user_id = user.id
        self.role_id = role.id


class Permission(db.Model):
    __tablename__ = 'permission'
    FOLLOW = 1 << 0
    COMMENT = 1 << 1
    WRITE_ARTICLES = 1 << 2
    MODERATE_COMMENTS = 1 << 3
    ADMINISTER = 0xff
