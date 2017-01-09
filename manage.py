#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.script import Manager, Server
import blog

app = blog.create_app(__name__)
manager = Manager(app)
manager.add_command("server", Server())


@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__ == "__main__":
    manager.run()
