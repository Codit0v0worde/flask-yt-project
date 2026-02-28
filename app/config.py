import os

class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = ROOT + UPLOAD_PATH

    DB_USER = os.environ.get('POSTGRES_USER', 'enginiger')
    DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '1')
    DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
    DB_NAME = os.environ.get('POSTGRES_DB', 'mydb')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SECRET_KEY = os.environ.get('SECRET_KEY', '2')
    SQLALCHEMY_TRACK_MODIFICATIONS = True