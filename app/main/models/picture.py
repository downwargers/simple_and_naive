#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from flask import current_app
from PIL import Image
from io import BytesIO
import os
import hashlib

allow_formats = ('jpg', 'jpeg', 'png', 'gif')

class Picture(db.Model):
    __tablename__ = 'pictures'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    file_name = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    alive = db.Column(db.Boolean, default=True)

    def __init__(self, im, name=None, type='', size='XL'):
        if name:
            self.name = name
        else:
            self.name = hashlib.md5(os.urandom(21)).hexdigest()

        if isinstance(im, file):
            im = Image.open(BytesIO(im.read()))
        mime = im.format.lower()
        if mime not in allow_formats:
            raise IOError()

        if type == 'avatar':
            avatar_size = min(im.size)
            picture_center = (im.size[0] / 2, im.size[1] / 2)
            picture_center_part = (picture_center[0] - avatar_size / 2, picture_center[1] - avatar_size / 2, picture_center[0] + avatar_size / 2, picture_center[1] + avatar_size / 2)
            im = im.crop(picture_center_part)
            avavar_size = current_app.config['AVATAR_SIZE'].get('size')
            if avavar_size:
                im = im.resize((avavar_size, avavar_size))
                self.name += '_' + size
                self.file_name = self.name + '.jpg'
            im.save(os.path.join(current_app.config['IMAGE_DIR'], self.file_name), 'jpeg')
        else:
            self.file_name = self.name + '.' + mime
            im.save(os.path.join(current_app.config['IMAGE_DIR'], self.file_name), mime)

        image_file = open(os.path.join(current_app.config['IMAGE_DIR'], self.file_name), 'r').read()
        new_name = hashlib.md5(image_file).hexdigest() + '.' + self.file_name.split('.')[1]
        os.rename(os.path.join(current_app.config['IMAGE_DIR'], self.file_name), os.path.join(current_app.config['IMAGE_DIR'], new_name))
        self.file_name = new_name

        db.session.add(self)
        db.commit()

    def to_json(self):
        json_dict = {}
        json_dict['id'] = self.id
        json_dict['name'] = self.name
        json_dict['file_name'] = self.file_name
        json_dict['timestamp'] = self.timestamp
        return json_dict

    def get_image(self):
        file_path = os.path.join(current_app.config['IMAGE_DIR'], self.file_name)
        im = Image.open(file_path)
        return im
