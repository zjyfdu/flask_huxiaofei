# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, current_app, abort
from . import course
from .. import db
from ..models import User, Course, Role, Permission
from .forms import CourseForm
from PIL import Image
from flask_login import current_user, login_required
from datetime import datetime
import os
from werkzeug import secure_filename

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

@course.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editcourse(id):
    course = Course.query.get_or_404(id)
    if current_user != course.teacher and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = CourseForm()
    if form.validate_on_submit():
        course.title = form.title.data
        course.abstract = form.abstract.data
        course.introduction = form.introduction.data
        course.price = form.price.data
        course.mode = form.mode.data
        file = request.files[form.image.name]
        if file:
            if course.img_url:
                os.remove(os.path.join(current_app.static_folder, 'courseimg', os.path.split(course.img_url)[-1]))
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
        flash('课程已更新')
        return redirect(url_for('course.classes', id=course.id))
    form.title.data = course.title
    form.abstract.data = course.abstract
    form.introduction.data = course.introduction
    form.price.data = course.price
    form.mode.data = course.mode
    return render_template('course/editcourse.html', form=form)

@course.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
def removecourse(id):
    course = Course.query.get_or_404(id)
    if current_user != course.teacher and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    db.session.delete(course)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    flash('课程已删除')
    return redirect(url_for('course.college', collegename=current_user.collegename))