#!/usr/bin/python
# -*- coding:utf-8 -*-
import app

blog_app = app.create_app(__name__)

if __name__ == "__main__":
    blog_app.run(host="0.0.0.0", port=5000)
