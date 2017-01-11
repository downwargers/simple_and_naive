#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import render_template
from flask.ext.login import current_user
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html', current_user=current_user)
