#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()

mail = Mail()

moment = Moment()

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'