from flask import render_template, redirect, request, url_for, flash
from . import course
from .. import db
from ..models import User
# from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\

#
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.ping()
#         if not current_user.confirmed \
#                 and request.endpoint \
#                 and request.endpoint[:5] != 'auth.' \
#                 and request.endpoint != 'static':
#             return redirect(url_for('auth.unconfirmed'))


@course.route('/')
def index():
    return render_template('course/index.html')
