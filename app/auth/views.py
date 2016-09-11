# _*_ coding: utf-8 _*_

from flask import render_template, redirect, request, url_for, flash, abort
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db, weibo_client
from ..models import User, Authorization, Oauth
from .forms import LoginForm, RegistrationForm, EditProfileForm
from flask.ext.login import current_user
from ..decorators import admin_required, permission_required
from hashlib import md5
import requests


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    # 如果当前用户已经登录直接重定向到用户首页
    if current_user.is_authenticated:
        flash(u'您已经登录了')
        return redirect(url_for('auth.user', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.authorization.verify_password(form.password.data):
            login_user(user, True)
            flash(u'欢迎回来 {0}！'.format(user.username or 'wb_' + user.oauth.weibo_user_id))
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或者密码错误。')
    # qq_uri = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=1105610021&redirect_uri=http://tetewechat.ngrok.cc/oauth/qq&state=test'
    return render_template('signin.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_auth = Authorization(password=form.password.data)
        new_user = User(email=form.email.data,
                        username=form.username.data,
                        authorization=new_auth
                        )
        db.session.add(new_user)
        flash(u'注册成功，现在可以登录了。')
        return redirect(url_for('auth.signin'))
    return render_template('signup.html', form=form)


@auth.route('/signout')
@login_required
def signout():
    logout_user()
    flash(u'已成功注销。')
    return redirect(url_for('main.index'))


@auth.route('/oauth/weibo')
def weibo():
    auth_code = request.args.get('code')
    if auth_code:
        r = weibo_client.request_access_token(auth_code)
        weibo_access_token = r.access_token
        weibo_expires_in = r.expires_in  # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
        weibo_user_id = r.uid  # 用户的新浪微博uid
        weibo_client.set_access_token(weibo_access_token, weibo_expires_in)
        oauth = Oauth.query.filter_by(weibo_user_id=weibo_user_id).first()
        if oauth:
            user = User.query.filter_by(oauth=oauth).first()
            login_user(user, True)
            flash(u'已使用微博帐号登录')
        else:
            oauth = Oauth(weibo_access_token=weibo_access_token,
                          weibo_expires_in=weibo_expires_in,
                          weibo_user_id=weibo_user_id
                          )
            # username = "weibo_" + weibo_user_id
            user = User(oauth=oauth)
            db.session.add(user)
            db.session.commit()
            login_user(user, True)
            flash(u'第一次使用微博登录，您可以去完善用户信息或者绑定已有帐号')
        return redirect(url_for('main.index'))
    else:
        return redirect(weibo_client.get_authorize_url())


@auth.route('/oauth/qq')
def qq():
    auth_code = request.args.get('code')
    r = requests.get('https://graph.qq.com/oauth2.0/authorize?grant_type=refresh_token&client_id=1105610021&client_secret=GbUsqMW5BjlJO8NN&code={}&redirect_uri=http://tetewechat.ngrok.cc/oauth/qq'.format(auth_code))
    print r.text


# 用户个人页面
@auth.route('/user/<user_id>')
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


# 编辑用户个人资料页面
@auth.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        avatar_filename = md5(current_user.username or current_user.oauth.weibo_user_id).hexdigest() + form.avatar.data.filename.strip('.')[-1]
        form.avatar.data.save('app/static/avatar/' + avatar_filename)
        current_user.nickname = form.name.data
        current_user.avatar = avatar_filename
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的资料已成功更新!')
        return redirect(url_for('.user', user_id=current_user.id))
    form.name.data = current_user.nickname
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@auth.route('/edit-profile-admin', methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin():
    pass


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
