#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
main = Blueprint('main', __name__)

from ..auth.models.permission import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import views, errors
