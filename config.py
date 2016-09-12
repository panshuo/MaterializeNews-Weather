import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self):
        pass

    SECRET_KEY = os.environ.get('SECRET_KEY') or '$%^NB4%^#_+UHha'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WEIBO_APP_KEY = '3797168746'
    WEIBO_APP_SECRET = 'cf1eb69ab2ea726b1b0542da97160c52'
    WEIBO_CALLBACK_URI = 'http://tetewechat.ngrok.cc/oauth/weibo'
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'mysql://peter:peter@127.0.0.1:3306/tete'
    @staticmethod
    def init_app(app):
        pass
