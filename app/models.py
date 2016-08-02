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
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return 'Role {0}'.format(self.name)


# 定义用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter  # 将用户密码的 Hash 值写入数据库
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 验证用户密码
        return check_password_hash(self.password_hash, password)

    def ping(self):  # 更新用户最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return 'User {0}'.format(self.username)


# 存储获取的新闻网站RSS文章
class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    published = db.Column(db.String)
    summary = db.Column(db.Text)
    media_thumbnail = db.Column(db.String)
    link = db.Column(db.String)
    news_agency = db.Column(db.String)

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
