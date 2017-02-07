#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import FlaskForm
from flask.ext.login import current_user
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Length, DataRequired, Email, Regexp
from wtforms.widgets import CheckboxInput, ListWidget

from ..auth.models.user import User
from ..auth.models.role import Role
from ..auth.models.permission import Permission


class EditProfileForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired(), Length(1, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = current_user

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

def check_edit_profile_data(json_data):
    form = EditProfileForm(meta={"csrf": False})
    form.username.data = json_data.get('username')
    form.about_me.data = json_data.get('about_me')
    return form.validate()

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    #roles = SelectMultipleField('Role', coerce=int, option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    #permissions = SelectMultipleField('Permission', coerce=int, option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        #self.roles.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        #self.permissions.choices = [(permission.id, permission.name) for permission in Permission.query.order_by(Permission.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

def check_edit_profile_admin_data(json_data, user):
    form = EditProfileAdminForm(user, meta={"csrf": False})
    form.email.data = json_data.get('email')
    form.username.data = json_data.get('username')
    form.confirmed.data = json_data.get('confirmed')
    form.about_me.data = json_data.get('about_me')
    return form.validate()

class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

def check_post_data(json_data, user):
    form = PostForm(user, meta={"csrf": False})
    form.body.data = json_data.get('body')
    return form.validate()