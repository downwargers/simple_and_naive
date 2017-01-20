#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db
from ...tools import ManyToMany
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
