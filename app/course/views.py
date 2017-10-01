from flask import render_template, redirect, request, url_for, flash, current_app
import flask_bootstrap
from . import course
from .. import db
from ..models import User, Course
from .forms import CourseForm
from PIL import Image
from flask_login import current_user
from datetime import datetime
import os
from werkzeug import secure_filename

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
        course = Course(title=form.title.data,
                        abstract=form.abstract.data,
                        introduction=form.introduction.data,
                        price=form.price.data,
                        mode=form.mode.data,
                        teacher=current_user,
                        timestamp=datetime.now())
        file = request.files[form.image.name]
        if file:
            size = (240, 140)
            im = Image.open(file)
            im.thumbnail(size)
            filename = secure_filename(file.filename)
            im.save(os.path.join(current_app.static_folder, 'courseimg', filename))
            course.img_url = url_for('static', filename='%s/%s' % ('avatar', filename))
        db.session.add(course)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('course.index'))
    return render_template('course/addcourse.html', form=form)