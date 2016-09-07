import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self):
        pass

    SECRET_KEY = os.environ.get('SECRET_KEY') or '$%^NB4%^#_+UHha'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WEIBO_APP_KEY = '4218865242'
    WEIBO_APP_SECRET = 'aba62c8ec764b2b6bfd426e6d1dfdddb'
    WEIBO_CALLBACK_URI = 'http://tetewechat.ngrok.cc/auth/weibo/'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @staticmethod
    def init_app(app):
        pass

