#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
import blog

app = blog.create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, blog.db)

manager.add_command('db', MigrateCommand)
manager.add_command("server", Server())


@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__ == "__main__":
    manager.run()
