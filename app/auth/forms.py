#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from .models.user import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

def check_login_data(json_data):
    form = LoginForm(meta={"csrf": False})
    form.email.data = json_data.get('email')
    form.password.data = json_data.get('password')
    form.remember_me.data = json_data.get('remember_me')
    return form.validate()


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

def check_registration_data(json_data):
    form = RegistrationForm(meta={"csrf": False})
    form.email.data = json_data.get('email')
    form.username.data = json_data.get('username')
    form.password.data = json_data.get('password')
    form.password2.data = json_data.get('password2')
    return form.validate()