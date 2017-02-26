#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask.ext.wtf import FlaskForm
from flask.ext.login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from .models.user import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    @staticmethod
    def check(json_data):
        form = LoginForm(meta={"csrf": False})
        form.email.data = json_data.get('email')
        form.password.data = json_data.get('password')
        form.remember_me.data = json_data.get('remember_me')
        return form.validate(), form.errors


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError('Username already in use.')

    @staticmethod
    def check(json_data):
        form = RegistrationForm(meta={"csrf": False})
        form.email.data = json_data.get('email')
        form.username.data = json_data.get('username')
        form.password.data = json_data.get('password')
        form.password2.data = json_data.get('password2')
        return form.validate(), form.errors


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

    @staticmethod
    def check(json_data):
        form = EditProfileForm(meta={"csrf": False})
        form.username.data = json_data.get('username')
        form.about_me.data = json_data.get('about_me')
        return form.validate(), form.errors


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    @staticmethod
    def check(json_data, user):
        form = EditProfileAdminForm(user, meta={"csrf": False})
        form.email.data = json_data.get('email')
        form.username.data = json_data.get('username')
        form.confirmed.data = json_data.get('confirmed')
        form.about_me.data = json_data.get('about_me')
        return form.validate(), form.errors


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_password(self, field):
        if self.user.verify_password(field.data):
            raise ValidationError('User`s password is wrong.')

    @staticmethod
    def check(json_data, user):
        form = ChangePasswordForm(user, meta={"csrf": False})
        form.old_password.data = json_data.get('old_password')
        form.password.data = json_data.get('password')
        form.password2.data = json_data.get('password2')
        return form.validate(), form.errors


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data, alive=True).first() is None:
            raise ValidationError('Unknown email address.')

    @staticmethod
    def check(json_data, user):
        form = ChangePasswordForm(user, meta={"csrf": False})
        form.email.data = json_data.get('email')
        return form.validate(), form.errors
