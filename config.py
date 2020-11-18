# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 - zinken7
"""
from os.path import join, dirname, realpath
from decouple import config

class Config(object):

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default=b'\x07\x8b\x94G\x8e\xcb\xc9\xbb\xcd\x1cS\xa9agX\xef')
    UPLOAD_MEDIA = 'app/static/uploads/media'
    UPLOAD_FILE = 'app/static/uploads/files'
    ALLOWED_EXTENSIONS = {'csv', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}
    
    DOWNLOAD_FILE = join(dirname(realpath(__file__)), 'app/static/downloads')

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY  = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config( 'DB_ENGINE'   , default='postgresql'    ),
        config( 'DB_USERNAME' , default='postgres'      ),
        config( 'DB_PASS'     , default='postgres'      ),
        config( 'DB_HOST'     , default='localhost'     ),
        config( 'DB_PORT'     , default=5432            ),
        config( 'DB_NAME'     , default='fb-pro'        )
    )

class DebugConfig(Config):
    DEBUG = True

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config( 'DB_ENGINE'   , default='postgresql'    ),
        config( 'DB_USERNAME' , default='postgres'      ),
        config( 'DB_PASS'     , default='postgres'      ),
        config( 'DB_HOST'     , default='localhost'     ),
        config( 'DB_PORT'     , default=5432            ),
        config( 'DB_NAME'     , default='fb-dev'        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}