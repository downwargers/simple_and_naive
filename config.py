#!/usr/bin/python
# -*- coding:utf-8 -*-


class Config(object):
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    Debug = True
    SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@127.0.0.1:5432/blogtext'


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}