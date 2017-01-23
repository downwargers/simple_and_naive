#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime

import bleach
from markdown import markdown

from ...auth.models.user import User
from app import db


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer)
    body_html = db.Column(db.Text)

    @property
    def author(self):
        return User.query.filter(User.id == self.author_id).first()

    @author.setter
    def author(self, val):
        self.author = val.id
        db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
