#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db


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
