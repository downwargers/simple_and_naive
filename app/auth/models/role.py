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

    permissions = ManyToMany(db, Permission, RolePermissionRelation, 'role_id', 'permission_id')
    
    def append_permissions(self, permission_ids_to_add):
        relations = RolePermissionRelation.query.filter(RolePermissionRelation.role_id == self.id).all()
        existed_roles_id = [relation.id for relation in relations]
        name_id_dict = {permission.name: permission.id for permission in Permission.query.all()}
        if not isinstance(permission_ids_to_add, list):
            permission_ids_to_add = [permission_ids_to_add]
        permission_ids_to_add = [standardize_instance(permission_id_to_add, Permission, name_id_dict) for permission_id_to_add in permission_ids_to_add]
        permission_ids_to_add = [permission_id_to_add for permission_id_to_add in permission_ids_to_add if permission_id_to_add and permission_id_to_add not in existed_roles_id]
        relations_to_add = [RolePermissionRelation(role_id=self.id, permission_id=permission_id_to_add) for permission_id_to_add in permission_ids_to_add]
        self.db.session.add_all(relations_to_add)

    def delete_permissions(self, permission_ids_to_del):
        relations = RolePermissionRelation.query.filter(RolePermissionRelation.role_id == self.id).all()
        existed_roles_id = [relation.id for relation in relations]
        name_id_dict = {permission.name: permission.id for permission in Permission.query.all()}
        if not isinstance(permission_ids_to_del, list):
            permission_ids_to_del = [permission_ids_to_del]

        permission_ids_to_del = [standardize_instance(permission_id_to_del, Permission, name_id_dict) for permission_id_to_del in permission_ids_to_del]
        permission_ids_to_del = [permission_id_to_del for permission_id_to_del in permission_ids_to_del if permission_id_to_del and permission_id_to_del in existed_roles_id]
        relations_to_del = RolePermissionRelation.filter(RolePermissionRelation.role_id == self.id).filter(RolePermissionRelation.permission_id.in_(permission_ids_to_del)).all()
        for relation in relations_to_del:
            self.db.session.delete(relation)
    
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
            role.permissions = Permission.query.filter(Permission.name.in_(permissions)).all()
            db.session.commit()
