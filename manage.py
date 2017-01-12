#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db
from app.auth.models import User, Role, Permission


app = create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("server", Server())


@manager.command
def create_administrator():
    print "####### CREATE ADMINISTRATOR #######"
    username = raw_input("Username (leave blank to use 'administrator'):") or "administrator"
    email = raw_input("Email address:")
    password = raw_input("Password:")
    re_password = raw_input("Password (again):")
    if password == re_password:
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print "Superuser created successfully."
    else:
        print "The two password are not same!"


@manager.command
def deploy():
    Permission.insert_permissions()
    Role.insert_roles()


if __name__ == "__main__":
    manager.run()
