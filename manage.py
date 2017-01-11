#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db


blog_app = create_app(__name__)
manager = Manager(blog_app)
migrate = Migrate(blog_app, db)


manager.add_command('db', MigrateCommand)
manager.add_command("server", Server())


@manager.shell
def make_shell_context():
    return dict(app=blog_app)

if __name__ == "__main__":
    manager.run()
