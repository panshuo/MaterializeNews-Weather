# _*_ coding: utf-8 _*_

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from flask.ext.login import current_user
from oauth2client import client
from googleapiclient.discovery import build
import httplib2, json, socks
from httplib2 import ProxyInfo

flow = client.flow_from_clientsecrets('/home/peter16/MaterializeNews-Weather-Google/client_secret.json',
                                      scope = 'profile',
                                      redirect_uri = 'http://tetewechat.ngrok.cc/googleoauth2'
                                      )


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或者密码错误。')
    # if form_up.validate_on_submit():
    #     new_user = User(email=form_up.email.data, username=form_up.username.data, password=form_up.password.data)
    #     db.session.add(new_user)
    #     flash(u'注册成功，现在可以登录了。')
    #     return redirect(url_for('auth.signin'))
    auth_uri = flow.step1_get_authorize_url()
    return render_template('signin.html', form=form, auth_uri=auth_uri)


@auth.route('/signout')
@login_required
def signout():
    logout_user()
    flash(u'已成功注销。')
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        flash(u'注册成功，现在可以登录了。')
        return redirect(url_for('auth.signin'))
    return render_template('signup.html', form=form)


@auth.route('/googleoauth2')
def google_oauth2():
    auth_code = request.args.get('code', None)
    if auth_code:
        credentials = flow.step2_exchange(code=auth_code, http=httplib2.Http(proxy_info=ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host='localhost', proxy_port=1080)))
        http_auth = credentials.authorize(httplib2.Http(proxy_info=ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host='localhost', proxy_port=1080)))
        drive_service = build('drive', 'v2', http_auth)
        files = drive_service.files().list().execute()
        return json.dumps(files)
    # user = User.query.filter_by(google_id=userinfo['id']).first()
    # if user:
    #     user.name = userinfo['name']
    #     user.avatar = userinfo['picture']
    # else:
    #     user = User(google_id=userinfo['id'],
    #                 name=userinfo['name'],
    #                 avatar=userinfo['picture'])
    # db.session.add(user)
    # db.session.flush()
    # login_user(user)
    # return redirect(url_for('index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
