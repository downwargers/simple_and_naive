#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db
from datetime import datetime


class UserRoleRelation(db.Model):
    __tablename__ = 'user_role_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class UserPermissionRelation(db.Model):
    __tablename__ = 'user_permission_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))


class RolePermissionRelation(db.Model):
    __tablename__ = 'role_permission_relation'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))


class FollowRelation(db.Model):
    __tablename__ = 'follow_relation'
    id = db.Column(db.Integer, primary_key=True)
    followee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    '''def __init__(self, followee_id, follower_id):
        self.followee_id = followee_id
        self.follower_id = follower_id'''
