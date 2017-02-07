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
    body = db.Column(db.text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    alive = db.Column(db.Boolean, default=True)

    def to_json(self):
        json_dict = {''}
        json_dict['id'] = self.id
        json_dict['body'] = self.body
        json_dict['timestamp'] = self.timestamp
        json_dict['author_id'] = self.author_id
        json_dict['author'] = self.author.to_json()
        return json_dict

db.event.listen(Post.body, 'set', Post.on_changed_body)
