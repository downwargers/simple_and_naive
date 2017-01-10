#!/usr/bin/python
# -*- coding:utf-8 -*-


class Config(object):
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    Debug = True
    cfg_file_name = 'blog_dev_cfg.json'


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
