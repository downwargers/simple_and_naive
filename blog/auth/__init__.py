#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
auth = Blueprint('auth', __name__, template_folder="templates", static_url_path='', static_folder='')
from . import views
