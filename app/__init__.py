# _*_ coding: utf-8 _*_

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
import time


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.signin'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    @app.template_filter('strftimestring')
    def format_time_string(value):
        raw_time = str(value)[:-7]
        time_array = time.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
        return time.strftime("%H:%M:%S", time_array)

    @app.template_filter('strftimestamp')
    def format_timestamp(value):
        return time.strftime("%H:%M:%S", time.localtime(value))

    return app
