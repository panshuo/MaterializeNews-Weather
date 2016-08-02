# _*_ coding: utf-8 _*_

from flask import render_template
from . import main


# @main.app_errorhandler(404)
# def page_not_found(f):
#     if f:
#         pass
#     return render_template('404.html'), 404
#
#
# @main.app_errorhandler(500)
# def internal_error(exception):
#     main.logger.error(exception)
#     return render_template('500.html'), 500
