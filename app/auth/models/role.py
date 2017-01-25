#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db
from ...tools import ManyToMany, standardize_instance
from .permission import Permission
from .relations import RolePermissionRelation


class Role(db.Model):
    __tablename__ = 'roles'
    USER = 'User'
    MODERATOR = 'Moderator'
    ADMINISTRATOR = 'Administrator'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)

    permissions = db.relationship('Permission', secondary='role_permission_relation', backref=db.backref('roles', lazy='dynamic'), lazy='dynamic')
    
    def append_permission(self, permission_names):
        if not isinstance(permission_names, list):
            permission_names = [permission_names]
        permissions = {permission.name: permission for permission in Permission.query.all()}
        for permission_name in permission_names:
            if isinstance(permission_name, Permission):
                permission = permission_name
            else:
                permission = permissions.get(permission_name)
            if permission:
                self.permissions.append(permission)
        db.session.add(self)

    def remove_permissions(self, permission_names):
        if permission_names == 'all':
            permission_names = self.permissions.all()
        if not isinstance(permission_names, list):
            permission_names = [permission_names]
        permissions = {permission.name: permission for permission in self.permissions.all()}
        for permission_name in permission_names:
            if isinstance(permission_name, Permission):
                permission = permission_name
            else:
                permission = permissions.get(permission_name)
            if permission in self.permissions:
                self.permissions.append(permission)
        db.session.add(self)
    
    def can(self, permission_name):
        if isinstance(permission_name, list):
            return all([self.can(p) for p in permission_name])
        return permission_name in [permission.name for permission in self.permissions.all()]

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
            role.append_permission(permissions)
            db.session.commit()
