# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path
from decouple import config

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_PASSWORD': config('REDIS_PASSWORD'),
    'CACHE_REDIS_URL': 'redis://localhost:6379'
    })

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)

def register_blueprints(app):
    for module_name in ('api', 'auth', 'admin'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def configure_logs(app):
    # soft logging
    try:
        basicConfig(filename='error.log', level=DEBUG)
        logger = getLogger()
        logger.addHandler(StreamHandler())
    except:
        pass

def handler_all_errors(app):
    # handle all errors before register blueprints
    @app.errorhandler(401)
    def access_forbidden(error):
        return render_template('errors/page_401.html'), 401

    @app.errorhandler(403)
    def access_forbidden(error):
        return render_template('errors/page_403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/page_404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/page_500.html'), 500

def create_app(config):
    app = Flask(__name__, subdomain_matching=True, static_folder='static')
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    handler_all_errors(app)
    configure_logs(app)
    return app
