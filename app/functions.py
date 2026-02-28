import secrets
import os.path

from PIL import Image
from flask import current_app


def save_picture(picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(picture.filename)
    picture_fn=random_hex+f_ext
    picture_path= os.path.join(current_app.config['SERVER_PATH'], picture_fn)
    output_size=(125,125)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def recursive_flattern_iterator(d):
    for k,v in d.items():
        if isinstance(v,list):
            yield v
        if isinstance(v,dict):
            yield from recursive_flattern_iterator(v)