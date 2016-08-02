# _*_ coding: utf-8 _*_

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from flask.ext.login import current_user


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
    return render_template('signin.html', form=form)


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


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
