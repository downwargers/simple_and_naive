#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from flask import current_app


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.now())
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    alive = db.Column(db.Boolean, default=True)

    def to_json(self, with_author=False, with_comment=False, comment_page=1):
        json_dict = {}
        json_dict['id'] = self.id
        json_dict['body'] = self.body
        json_dict['timestamp'] = self.timestamp
        json_dict['author_id'] = self.author_id
        if with_author:
            json_dict['author'] = self.author.to_json(lazy=True)
        if with_comment:
            pagination = self.comments.order_by('timestamp desc').paginate(comment_page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
            comments = pagination.items
            comments = [comment.to_json() for comment in comments]
            json_str = {'comments': comments, 'page': pagination.page, 'pages': pagination.pages, 'per_page': current_app.config['POSTS_PER_PAGE']}
            json_dict['comments'] = json_str
        return json_dict
