#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEV = False
    TEST = False
    PROD = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 15
    FOLLOWERS_PER_PAGE = 20

    AVATAR_SIZE = {
        'XL': (200, 200),
        'L': (50, 50),
        'S': (25, 25),
    }
    IMAGE_DIR = 'app/upload/image'
    DEFAULT_AVATAR = 'default_avatar'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEV = True
    DEBUG = True
    FLASK_ADMIN = 'downwargers@163.com'
    MAIL_SUBJECT_PREFIX = '[Simple and Naive]'
    MAIL_SENDER = 'Simple and Naive Admin <downwargers@163.com>'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    HOST = '127.0.0.1'
    PORT = 5000
    cfg_file_name = 'blog_dev_cfg.json'


class TestingConfig(Config):
    TEST = True
    cfg_file_name = 'blog_test_cfg.json'
    pass


class ProductionConfig(Config):
    PROD = True
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
