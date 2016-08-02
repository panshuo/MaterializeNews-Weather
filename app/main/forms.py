# _*_ coding: utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length


class EditProfileForm(Form):
    name = StringField(u'姓名', validators=[DataRequired(), Length(1, 64)])
    location = StringField(u'地址', validators=[DataRequired(), Length(1, 64)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')


class FetchNewsForm(Form):
    # agency = SelectField(choices=[("1", "BBC"), ("2", "SKY")], default=["1", "2"])
    count = IntegerField(u'抓取数量', validators=[DataRequired()])
    submit = SubmitField(u'开始抓取')
