#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask.ext.mail import Message
from blog import mail
from flask import render_template, current_app


def send_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject, sender=current_app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)