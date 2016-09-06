# _*_ coding: utf-8 _*_

from flask import render_template, redirect, request, url_for, flash, abort
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db, weibo_client
from ..models import User, Authorization
from .forms import LoginForm, RegistrationForm, EditProfileForm
from flask.ext.login import current_user
from ..decorators import admin_required, permission_required
from hashlib import md5


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print user.authorization
        print user.authorization[0]
        if user is not None and user.authorization[0].verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(u'欢迎回来 {0}！'.format(user.username))
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或者密码错误。')
    # auth_uri = flow.step1_get_authorize_url()
    return render_template('signin.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_auth = Authorization(password=form.password.data)
        new_user = User(email=form.email.data, username=form.username.data, authorization=[new_auth])
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


# @auth.route('/google-oauth2')
# def google_oauth2():
#     auth_code = request.args.get('code', None)
#     if auth_code:
#         credentials = flow.step2_exchange(code=auth_code, http=httplib2.Http(proxy_info=ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host='localhost', proxy_port=1080)))
#         http_auth = credentials.authorize(httplib2.Http(proxy_info=ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host='localhost', proxy_port=1080)))
#         drive_service = build('drive', 'v2', http_auth)
#         files = drive_service.files().list().execute()
#         return json.dumps(files)
#     user = User.query.filter_by(google_id=userinfo['id']).first()
#     if user:
#         user.name = userinfo['name']
#         user.avatar = userinfo['picture']
#     else:
#         user = User(google_id=userinfo['id'],
#                     name=userinfo['name'],
#                     avatar=userinfo['picture'])
#     db.session.add(user)
#     db.session.flush()
#     login_user(user)
#     return redirect(url_for('index'))


@auth.route('/weibo-oauth2')
def weibo_oauth2():
    auth_code = request.args.get('code', None)
    if auth_code:
        r = weibo_client.request_access_token(auth_code)
        access_token = r.access_token
        expires_in = r.expires_in  # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
        # TODO: 在此可保存access token
        print access_token, expires_in
        weibo_client.set_access_token(access_token, expires_in)
        return "sucsess!"


# 用户个人页面
@auth.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    url = weibo_client.get_authorize_url()
    return render_template('user.html', user=user, url=url)


# 编辑用户个人资料页面
@auth.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        avatar_filename = md5(current_user.email).hexdigest() + form.avatar.data.filename.strip('.')[-1]
        print avatar_filename
        form.avatar.data.save('app/static/avatar/' + avatar_filename)
        current_user.nickname = form.name.data
        current_user.avatar = avatar_filename
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的资料已成功更新!')
        return redirect(url_for('.user', username=current_user.username))
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
