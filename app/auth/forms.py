# _*_ coding: utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..models import User, Authorization


class LoginForm(Form):
    email = StringField(u'电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(6)])
    remember_me = BooleanField(u'保持登录状态')
    submit = SubmitField(u'登录')


class RegistrationForm(Form):
    email = StringField(u'电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'电子邮箱地址已经被使用。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被使用。')


class EditProfileForm(Form):
    name = StringField(u'姓名', validators=[DataRequired(), Length(1, 64)])
    location = StringField(u'地址', validators=[DataRequired(), Length(1, 64)])
    about_me = TextAreaField(u'个人简介')
    avatar = FileField(u'头像')
    submit = SubmitField(u'提交')