#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask
from config import config
from extensions import db, mail, login_manager, pagedown, cors
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from log import logger, init_logging
import json
import os


def create_app(name, config_name='development'):
    app = Flask(name)
    app.root_path = os.path.dirname(os.path.abspath(__file__))
    app.config.from_object(config[config_name])

    fd = open(config[config_name].cfg_file_name, 'r')
    cfg = json.loads(fd.read())
    app.config.from_mapping(cfg)

    config[config_name].init_app(app)
    init_logging(logger, cfg)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint, url_prefix='')
    # attach routes and custom error pages here
    return app


