#!/usr/bin/python
# -*- coding:utf-8 -*-
from ... import db


class Permission(db.Model):
    __tablename__ = 'permissions'
    FOLLOW = "FOLLOW"
    COMMENT = "COMMENT"
    WRITE_ARTICLES = "WRITE_ARTICLES"
    MODERATE_COMMENTS = "MODERATE_COMMENTS"
    ADMINISTER = "ADMINISTER"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    @staticmethod
    def insert_permissions():
        permissions = [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE_ARTICLES, Permission.MODERATE_COMMENTS, Permission.ADMINISTER]
        for p in permissions:
            permission = Permission.query.filter(Permission.name == p).first()
            if permission is None:
                permission = Permission(name=p)
            db.session.add(permission)
            db.session.commit()

