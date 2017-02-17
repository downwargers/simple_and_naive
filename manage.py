#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Server, Shell

import app
from app import create_app, db
from app.auth.forms import check_registration_data
from app.auth.models.user import User
from app.auth.models.role import Role
from app.auth.models.permission import Permission
from app.auth.models.relations import FollowRelation, RolePermissionRelation, UserPermissionRelation, UserRoleRelation
from app.main.models.picture import Picture
from app.main.models.post import Post
from app.main.models.comment import Comment

app = create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, FollowRelation=FollowRelation, UserRoleRelation=UserRoleRelation, UserPermissionRelation=UserPermissionRelation, RolePermissionRelation=RolePermissionRelation, Post=Post, Comment=Comment, Picture=Picture)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("server", Server(host=app.config['HOST'], port=app.config['PORT']))


@manager.command
def create_administrator():
    print "####### CREATE ADMINISTRATOR #######"
    username = raw_input("Username (leave blank to use 'administrator'):") or "administrator"
    email = raw_input("Email address (leave blank to use '" + app.config['FLASK_ADMIN'] + "'):") or app.config['FLASK_ADMIN']
    password = raw_input("Password:")
    re_password = raw_input("Password (again):")

    administrator_json = {"email": email, "username": username, "password": password, "password2": re_password}

    if check_registration_data(administrator_json):
        user = User(email=email, username=username, password=password, confirmed=True)
        user.set_roles(Role.ADMINISTRATOR)
        db.session.add(user)
        db.session.commit()
        print "Administrator created successfully."
    else:
        print "Fail to create Administrator!"


@manager.command
def deploy():
    Permission.insert_permissions()
    Role.insert_roles()

    for size in app.config['AVATAR_SIZE']:
        Picture(app.config['DEFAULT_AVATAR_FILE'], name=app.config['DEFAULT_AVATAR'], type='avatar', size=size)


if __name__ == "__main__":
    manager.run()
