#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Server, Shell

import app
from app import create_app, db
from app.auth.forms import RegistrationForm
from app.auth.models.user import User
from app.auth.models.role import Role
from app.auth.models.permission import Permission

app = create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)
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
    form = RegistrationForm(meta={"csrf": False})
    form.email.data = email
    form.username.data = username
    form.password.data = password
    form.password2.data = re_password

    print form
    print form.validate()
    if form.validate():
        user = User(email=email, username=username, password=password, confirmed=True)
        db.session.add(user)
        db.session.commit()
        user.roles.append(Role.ADMINISTRATOR)
        db.session.commit()
        print "Administrator created successfully."
    else:
        print form.errors
        print "Fail to create Administrator!"


@manager.command
def deploy():
    Permission.insert_permissions()
    Role.insert_roles()


if __name__ == "__main__":
    manager.run()
