from flask import render_template, redirect, request, url_for, flash
import wtforms
from . import course
from .. import db
from ..models import User
from .forms import CourseForm

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

@course.route('/class/<int:id>', methods=['GET', 'POST'])
def classes(id):
    return render_template('course/class.html', id=id)

@course.route('/addcourse', methods=['GET', 'POST'])
def addcourse():
    form = CourseForm()
    if form.validate_on_submit():
        print 'yes'
    return render_template('course/addcourse.html', form=form)

