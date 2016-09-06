# _*_ coding: utf-8 _*_

from flask import render_template, redirect, url_for, flash, request
from flask import abort
from flask.ext.login import current_user
from .. import db, weibo_client
from ..models import User, News, Weather
from ..decorators import admin_required, permission_required
from . import main
from flask.ext.login import login_required
from .forms import FetchNewsForm
from sqlalchemy import desc
from datetime import datetime as dt
from random import sample
from hashlib import md5

# 首页
@main.route('/', methods=['GET', 'POST'])
def index():
    # 刷新新闻数据库部分
    form = FetchNewsForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        News.fetch_news(form.count.data)
        return redirect(url_for('.index'))
    if form.validate_on_submit() and not current_user.is_authenticated:
        flash(u"抓取新闻之前请先登录。")
        return redirect(url_for('auth.signin'))

    # 幻灯片部分
    news_count = News.query.filter_by(news_agency='BBC').order_by(desc(News.id)).first().id  # 获取数据库中最后一条新闻的id
    selected_news = sample(range(news_count), 5)  # 随机获得5条新闻的id
    slider = []
    for news in selected_news:
        slider.append(News.query.filter_by(id=news).first())

    # 分页部分
    page = request.args.get('page', 1, type=int)
    pagination = News.query.order_by(desc(News.id)).paginate(page, per_page=8, error_out=False)
    articles = pagination.items

    # 天气部分
    access_time = dt.now()
    weather = {'tianjin': Weather.query.filter_by(city="Tianjin").order_by(desc(Weather.id)).first(),
               'beijing': Weather.query.filter_by(city="Beijing").order_by(desc(Weather.id)).first(),
               'shanghai': Weather.query.filter_by(city="Shanghai").order_by(desc(Weather.id)).first()}
    for city in weather:
        if not weather[city] or (access_time - weather[city].refresh_time).seconds > 3600:
            Weather.get_weather(city)

    return render_template("index.html",
                           articles=articles,
                           weather=weather,
                           form=form,
                           pagination=pagination,
                           slider=slider)


# 抓取新闻接口 默认50条
@main.route('/fetchnews', methods=['GET', 'POST'])
@login_required
def fetch_news():
    News.fetch_news(50)
    return redirect(url_for('.index'))

