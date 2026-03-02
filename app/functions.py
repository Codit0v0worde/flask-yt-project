import secrets
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app

def save_picture(picture):
    """
    Сохраняет аватар пользователя (изображение) в папку upload/,
    уменьшает до 125x125 пикселей и возвращает уникальное имя файла.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['SERVER_PATH'], picture_fn)

    output_size = (125, 125)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def save_comment_file(file):
    """
    Сохраняет файл, прикреплённый к комментарию.
    Возвращает уникальное имя файла.
    """
    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + '_' + filename
    upload_folder = os.path.join(current_app.config['ROOT'], 'static/uploads/comments')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return unique_name

def save_activity_file(file):
    """
    Сохраняет файл, прикреплённый к лекции или заданию (активности).
    Возвращает уникальное имя файла.
    """
    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + '_' + filename
    upload_folder = os.path.join(current_app.config['ROOT'], 'static/uploads/activities')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return unique_name

def save_submission_file(file):
    """
    Сохраняет файл ответа студента на задание.
    Возвращает уникальное имя файла.
    """
    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + '_' + filename
    upload_folder = os.path.join(current_app.config['ROOT'], 'static/uploads/submissions')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return unique_name

def recursive_flattern_iterator(d):
    """
    Рекурсивно обходит словарь и возвращает все значения-списки.
    Используется в bundles.py для сбора списков бандлов.
    """
    for k, v in d.items():
        if isinstance(v, list):
            yield v
        if isinstance(v, dict):
            yield from recursive_flattern_iterator(v)