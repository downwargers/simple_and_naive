#!/usr/bin/python
# -*- coding:utf-8 -*-
from wtforms import TextAreaField
from flask.ext.wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

    @staticmethod
    def check(json_data, user):
        form = PostForm(user, meta={"csrf": False})
        form.body.data = json_data.get('body')
        return form.validate(), form.errors


class CommentForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

    @staticmethod
    def check(json_data, user):
        form = PostForm(user, meta={"csrf": False})
        form.body.data = json_data.get('body')
        return form.validate(), form.errors
