#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from flask import current_app


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    reply_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    comments = db.relationship('Comment', backref=db.backref('parent_comment', remote_side=[id]), lazy='dynamic')
    alive = db.Column(db.Boolean, default=True)

    def to_json(self, with_author=False, cascading=False, comment_page=1):
        json_dict = {}
        json_dict['id'] = self.id
        json_dict['body'] = self.body
        json_dict['timestamp'] = self.timestamp
        json_dict['author_id'] = self.author_id
        if with_author:
            json_dict['author'] = self.author.to_json(lazy=True)
        if cascading and self.comments:
            pagination = self.comments.order_by('timestamp desc').paginate(comment_page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
            comments = pagination.items
            comments = [comment.to_json(with_author=with_author, cascading=cascading) for comment in comments]
            json_str = {'comments': comments, 'page': pagination.page, 'pages': pagination.pages, 'per_page': current_app.config['POSTS_PER_PAGE']}
            json_dict['comments'] = json_str

        return json_dict


