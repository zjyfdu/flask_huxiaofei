from flask import render_template, redirect, request, url_for, flash, current_app
import flask_bootstrap
from . import course
from .. import db
from ..models import User, Course, Role
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

# @main.route('/', methods=['GET', 'POST'])
# def index():
#
#     page = request.args.get('page', 1, type=int)
#     show_followed = False
#     if current_user.is_authenticated:
#         show_followed = bool(request.cookies.get('show_followed', ''))
#     if show_followed:
#         query = current_user.followed_posts
#     else:
#         query = Post.query
#     pagination = query.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#         error_out=False)
#     posts = pagination.items
#     return render_template('main/college.html', form=form, posts=posts,
#                            show_followed=show_followed, pagination=pagination)
@course.route('/')
def index():
    return redirect(url_for('course.college', collegename='chendian'))

@course.route('/college/<string:collegename>')
def college(collegename):
    page = request.args.get('page', 1, type=int)
    teacher_role = Role.query.filter_by(name='Teacher').first_or_404()
    query = User.query.filter_by(role=teacher_role, collegename=collegename).filter(User.teachercourse)
    pagination = query.paginate(page, per_page=5, error_out=False)
    teachers = pagination.items
    return render_template('course/college.html', teachers=teachers, pagination=pagination)

@course.route('/class/<int:id>', methods=['GET', 'POST'])
def classes(id):
    course = Course.query.get_or_404(id)
    return render_template('course/class.html', course=course)

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
            course.img_url = url_for('static', filename='%s/%s' % ('courseimg', filename))
        db.session.add(course)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('course.index'))
    return render_template('course/addcourse.html', form=form)