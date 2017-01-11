#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from app import db
from .models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if db.query(User).filter(User.email == field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if db.query(User).filter(User.username == field.data).first():
            raise ValidationError('Username already in use.')
