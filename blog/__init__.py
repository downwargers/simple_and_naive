#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask
from config import config
from extensions import db, moment, bootstrap, mail, login_manager
from .auth import auth as auth_blueprint
from .main import main as main_blueprint


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint, url_prefix='')
    # attach routes and custom error pages here
    return app
