#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown
from flask.ext.cors import CORS
from flask.ext.bootstrap import Bootstrap
import logging

mail = Mail()

db = SQLAlchemy()

pagedown = PageDown()

bootstrap = Bootstrap()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

cors = CORS()
logging.getLogger('flask_cors').level = logging.DEBUG
