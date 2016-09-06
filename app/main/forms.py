# _*_ coding: utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, Length


class FetchNewsForm(Form):
    # agency = SelectField(choices=[("1", "BBC"), ("2", "SKY")], default=["1", "2"])
    count = IntegerField(u'抓取数量', validators=[DataRequired()])
    submit = SubmitField(u'开始抓取')
