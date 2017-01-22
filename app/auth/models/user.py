#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db, login_manager
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from ...tools import ManyToMany, standardize_instance
from .role import Role
from .permission import Permission
from .relations import UserPermissionRelation, UserRoleRelation, FollowRelation


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

    def append_roles(self, role_ids_to_add):
        relations = UserRoleRelation.query.filter(UserRoleRelation.user_id == self.id).all()
        existed_roles_id = [relation.id for relation in relations]
        name_id_dict = {role.name: role.id for role in Role.query.all()}
        if not isinstance(role_ids_to_add, list):
            role_ids_to_add = [role_ids_to_add]
        role_ids_to_add = [standardize_instance(role_id_to_add, Role, name_id_dict) for role_id_to_add in role_ids_to_add]
        role_ids_to_add = [role_id_to_add for role_id_to_add in role_ids_to_add if role_id_to_add and role_id_to_add not in existed_roles_id]
        relations_to_add = [UserRoleRelation(user_id=self.id, role_id=role_id_to_add) for role_id_to_add in role_ids_to_add]
        self.db.session.add_all(relations_to_add)

    def delete_roles(self, role_ids_to_del):
        relations = UserRoleRelation.query.filter(UserRoleRelation.role_id == self.id).all()
        existed_roles_id = [relation.id for relation in relations]
        name_id_dict = {role.name: role.id for role in Role.query.all()}
        if not isinstance(role_ids_to_del, list):
            role_ids_to_del = [role_ids_to_del]

        role_ids_to_del = [standardize_instance(role_id_to_del, Role, name_id_dict) for role_id_to_del in role_ids_to_del]
        role_ids_to_del = [role_id_to_del for role_id_to_del in role_ids_to_del if role_id_to_del and role_id_to_del in existed_roles_id]
        relations_to_del = UserRoleRelation.filter(UserRoleRelation.user_id == self.id).filter(UserRoleRelation.role_id.in_(role_ids_to_del)).all()
        for relation in relations_to_del:
            self.db.session.delete(relation)

    permissions = ManyToMany(db, Permission, UserPermissionRelation, 'user_id', 'permission_id')

    def append_permissions(self, permission_ids_to_add):
        relations = UserPermissionRelation.query.filter(UserPermissionRelation.user_id == self.id).all()
        existed_permissions_id = [relation.id for relation in relations]
        name_id_dict = {permission.name: permission.id for permission in Permission.query.all()}
        if not isinstance(permission_ids_to_add, list):
            permission_ids_to_add = [permission_ids_to_add]
        permission_ids_to_add = [standardize_instance(permission_id_to_add, Permission, name_id_dict) for permission_id_to_add in permission_ids_to_add]
        permission_ids_to_add = [permission_id_to_add for permission_id_to_add in permission_ids_to_add if permission_id_to_add and permission_id_to_add not in existed_permissions_id]
        relations_to_add = [UserPermissionRelation(user_id=self.id, permission_id=permission_id_to_add) for permission_id_to_add in permission_ids_to_add]
        self.db.session.add_all(relations_to_add)

    def delete_permissions(self, permission_ids_to_del):
        relations = UserPermissionRelation.query.filter(UserPermissionRelation.permission_id == self.id).all()
        existed_permissions_id = [relation.id for relation in relations]
        name_id_dict = {permission.name: permission.id for permission in Permission.query.all()}
        if not isinstance(permission_ids_to_del, list):
            permission_ids_to_del = [permission_ids_to_del]

        permission_ids_to_del = [standardize_instance(permission_id_to_del, Permission, name_id_dict) for permission_id_to_del in permission_ids_to_del]
        permission_ids_to_del = [permission_id_to_del for permission_id_to_del in permission_ids_to_del if permission_id_to_del and permission_id_to_del in existed_permissions_id]
        relations_to_del = UserPermissionRelation.filter(UserPermissionRelation.user_id == self.id).filter(UserPermissionRelation.permission_id.in_(permission_ids_to_del)).all()
        for relation in relations_to_del:
            self.db.session.delete(relation)

    @declared_attr
    def followers(cls):
        return ManyToMany(db, cls, FollowRelation, 'followee_id', 'follower_id')

    @declared_attr
    def followees(cls):
        return ManyToMany(db, cls, FollowRelation, 'follower_id', 'followee_id')

    def follow(self, user):
        if not self.is_following(user):
            f = FollowRelation(follower_id=self.id, followee_id=user.id)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter(FollowRelation.follower_id==user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter(FollowRelation.follower_id==user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter(FollowRelation.followee_id==user.id).first() is not None

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