#!/usr/bin/python
# -*- coding:utf-8 -*-
import blog

app = blog.create_app(__name__)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=800)
