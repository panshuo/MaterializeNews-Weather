# _*_ coding: utf-8 _*_

from . import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from datetime import datetime
from feedparser import parse
import urllib
import requests
import time


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 定义用户角色模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return 'Role {0}'.format(self.name)

    @staticmethod
    def insert_roles():
        roles = {
            'Administrator': (0xff, False),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.MODIFY, False),
            'User': (Permission.FOLLOW | Permission.COMMENT, True)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


# 权限
class Permission:
    def __init__(self):
        pass

    FOLLOW = 0x01
    COMMENT = 0x02
    MODIFY = 0x04
    FETCH_NEWS = 0x08
    ADMINISTER = 0x80


# 用户和新闻 多对多关系模型
class Favourite(db.Model):
    __tablename__ = 'favourites'
    starred_news_id = db.Column(db.Integer, db.ForeignKey('news.id'), primary_key=True)
    starred_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())


# 定义用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # 普通登录模型 & Oauth 模型的一对一关系， 最后的 uselist 参数决定是一对一还是一对多关系
    authorization = db.relationship('Authorization', backref='user', uselist=False)
    oauth = db.relationship('Oauth', backref='user', uselist=False)

    # 和 News 模型的多对多关系
    starred_news = db.relationship('Favourite',
                                   foreign_keys=[Favourite.starred_by_id],
                                   backref=db.backref('starred_by', lazy='joined'),
                                   lazy='dynamic',
                                   cascade='all, delete-orphan'
                                   )
    # 外键，指向 Role 模型的主键
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # 用户属性
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    avatar = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    def can(self, permissions):  # 将用户的角色权限和传入的参数权限按位与，如果结果和传入的参数一样，说明用户具有这个参数传入的权限
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):  # 用 can 方法判断此用户是否为管理员（拥有所有的权限）
        return self.can(Permission.ADMINISTER)

    def ping(self):  # 更新用户最后访问时间
        self.last_seen = datetime.now()
        db.session.add(self)

    def star(self, news):
        if not self.is_starring(news):
            f = Favourite(favourite_news=news, favourite_by=self)
            db.session.add(f)

    def cancel_star(self, news):
        f = self.favourite_news.filter_by(favourite_news_id=news.id).first()
        if f:
            db.session.delete(f)

    def is_starring(self, news):
        return self.favourite_news.filter_by(favourite_news_id=news.id).first() is not None

    def __repr__(self):
        return u'User {0}'.format(self.username)


# 普通用户名密码方式登录
class Authorization(db.Model):
    __tablename__ = "authorization"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter  # 将用户密码的 Hash 值写入数据库
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 验证用户密码
        return check_password_hash(self.password_hash, password)


# 第三方 Oauth 2 登录
class Oauth(db.Model):
    __tablename__ = "oauths"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    weibo_access_token = db.Column(db.String(64))
    weibo_user_id = db.Column(db.String(16))
    weibo_expires_in = db.Column(db.Integer)


# 存储获取的新闻网站RSS文章
class News(db.Model):
    __tablename__ = "news"
    # 和 User 模型的多对多关系
    starred_by = db.relationship('Favourite',
                                   foreign_keys=[Favourite.starred_news_id],
                                   backref=db.backref('starred_news', lazy='joined'),
                                   lazy='dynamic',
                                   cascade='all, delete-orphan'
                                   )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    published = db.Column(db.String)
    summary = db.Column(db.Text)
    media_thumbnail = db.Column(db.String)
    link = db.Column(db.String)
    news_agency = db.Column(db.String)

    def star_by(self, user):
        return self.favourite_by.filter_by(favourite_by_id=user.id).first() is not None

    @staticmethod
    def fetch_news(count=20):
        rss_url = {"BBC": "http://feeds.bbci.co.uk/news/rss.xml"
                   # "SKY": "http://feeds.skynews.com/feeds/rss/world.xml"
                   # "ABC Top Stories": "http://feeds.abcnews.com/abcnews/topstories",
                   # "ABC Tech Headlines": "http://feeds.abcnews.com/abcnews/technologyheadlines",
                   # "theguardian": "https://www.theguardian.com/uk/rss"
                   }

        for agency in rss_url:
            feed = parse(rss_url[agency])
            for article in feed['entries'][0: count]:
                if not News.query.filter_by(title=article.get("title")).first():
                    if article.get("media_thumbnail"):
                        a = News(news_agency=agency, title=article.get("title"),
                                 published=article.get("published"),
                                 summary=article.get("summary"),
                                 media_thumbnail=article.get("media_thumbnail")[0]["url"],
                                 link=article.get("link")
                                 )
                        db.session.add(a)
                        db.session.commit()
                    else:
                        a = News(news_agency=agency, title=article.get("title"),
                                 published=article.get("published"),
                                 summary=article.get("summary"),
                                 link=article.get("link")
                                 )
                        db.session.add(a)
                        db.session.commit()


# 存储获取的天气
class Weather(db.Model):
    __tablename__ = "weather"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    city = db.Column(db.String, index=True)
    temperature = db.Column(db.String)
    temp_min = db.Column(db.String)
    temp_max = db.Column(db.String)
    description = db.Column(db.String)
    humidity = db.Column(db.Integer)
    sunset = db.Column(db.String)
    sunrise = db.Column(db.String)
    refresh_time = db.Column(db.DateTime, index=True)

    @staticmethod
    def get_weather(city):
        query = urllib.quote(city)
        api_url = "http://api.openweathermap.org/data/2.5/weather?" \
                  "q={0}&units=metric&appid=eb692863e7f06b01aaa1863a4fcdd753&lang=zh_cn".format(query)
        weather = requests.get(api_url).json()
        if weather.get("weather"):
            w = Weather(country=weather["sys"]["country"],
                        city=weather["name"],
                        temperature=weather["main"]["temp"],
                        description=weather["weather"][0]["description"],
                        temp_min=weather["main"]["temp_min"],
                        temp_max=weather["main"]["temp_max"],
                        humidity=weather["main"]["humidity"],
                        sunset=time.strftime(u"%H:%M", time.localtime(weather["sys"]["sunset"])),
                        sunrise=time.strftime(u"%H:%M", time.localtime(weather["sys"]["sunrise"])),
                        refresh_time=datetime.now()
                        )
            db.session.add(w)
            db.session.commit()
        print "成功!"
