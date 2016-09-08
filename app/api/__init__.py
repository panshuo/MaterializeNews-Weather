# _*_ coding: utf-8 _*_

from flask import Blueprint
api = Blueprint('api', __name__)
from . import views