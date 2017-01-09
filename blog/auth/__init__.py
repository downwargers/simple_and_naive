#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from . import views
auth = Blueprint('auth', __name__)
