#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask

from blog.config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


@app.route("/")
def home():
    return '<h1>Hello World!</h1>'

if __name__ == "__main__":
    app.run()
