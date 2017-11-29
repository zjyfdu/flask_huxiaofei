# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, current_app, abort, jsonify
from . import course
from .. import db
from ..models import User, Course, Role, Permission, Subject, School
from .forms import CourseForm, SubjectForm, ApproveForm
from PIL import Image
from flask_login import current_user, login_required
from datetime import datetime
import os
from werkzeug import secure_filename

@course.route('/')
def index():
    return redirect(url_for('course.college', collegename='chengdian'))

# @course.route('/college/<string:collegename>')
# def college(collegename):
#     page = request.args.get('page', 1, type=int)
#     teacher_role = Role.query.filter_by(name='Teacher').first_or_404()
#     query = User.query.filter_by(role=teacher_role, collegename=collegename).filter(User.teachercourse)
#     pagination = query.paginate(page, per_page=5, error_out=False)
#     teachers = pagination.items
#     return render_template('course/college.html', teachers=teachers, pagination=pagination)

@course.route('/college/<string:collegename>')
def college(collegename):
    page = request.args.get('page', 1, type=int)
    school = School.query.filter_by(collegename=collegename).first_or_404()
    query = Subject.query.filter_by(school=school)
    pagination = query.paginate(page, per_page=5, error_out=False)
    subjects = pagination.items
    return render_template('course/college.html', subjects=subjects, pagination=pagination)

@course.route('/class/<int:id>', methods=['GET', 'POST'])
def classes(id):
    course = Course.query.get_or_404(id)
    return render_template('course/class.html', course=course)

@course.route('/addsubject', methods=['GET', 'POST'])
def addsubject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(subjectname=form.title.data,
                          about_subject=form.about_subject.data,
                          )
        school = School.query.filter_by(collegename=form.school.data).first()
        subject.school = school
        db.session.add(subject)
        return redirect(url_for('course.college', collegename=form.school.data))
    return render_template('course/addsubject.html', form=form)

@course.route('/addcourse', methods=['GET', 'POST'])
def addcourse():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(title=form.title.data,
                        abstract=form.abstract.data,
                        introduction=form.introduction.data,
                        introduction2=form.introduction2.data,
                        price=form.price.data,
                        mode=form.mode.data,
                        teacher=current_user,
                        subject=current_user.subject,
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

@course.route('/joinincourse/<int:id>')
@login_required
def joinincourse(id):
    course = Course.query.get_or_404(id)
    if course not in current_user.studentscourses:
        current_user.studentscourses.append(course)
    db.session.add(current_user)
    return redirect(url_for('course.classes', id=id))


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
        course.introduction2 = form.introduction2.data
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
    form.introduction2.data = course.introduction2
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

@course.route('/subjectedit/<int:id>', methods=['GET', 'POST'])
@login_required
def editsubject(id):
    subject = Subject.query.get_or_404(id)
    if not current_user.is_administrator():
        abort(403)
    form = SubjectForm()
    if form.validate_on_submit():
        subject.about_subject = form.about_subject.data
        subject.subjectname = form.title.data
        subject.school = School.query.filter_by(collegename=form.school.data).first()
        db.session.add(subject)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        flash('专业信息已更新')
        return redirect(url_for('course.college', collegename=subject.school.collegename))
    form.about_subject.data = subject.about_subject
    form.school.data = subject.school.collegename
    form.title.data = subject.subjectname
    return render_template('course/editsubject.html', form=form)

@course.route('/subjectremove/<int:id>', methods=['GET', 'POST'])
@login_required
def removesubject(id):
    if not current_user.is_administrator():
        abort(403)
    subject = Subject.query.get_or_404(id)
    collegename = subject.school.collegename
    if not current_user.is_administrator():
        abort(403)
    db.session.delete(subject)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    flash('专业已删除')
    return redirect(url_for('course.college', collegename=subject.school.collegename))

# @course.route('/apply_for_professor', methods=['GET', 'POST'])
# @login_required
# def apply_for_professor():
#     try:
#         current_user.teacher_date=datetime.datetime.now()
#         db.session.add(current_user)
#         flash('申请成功！管理员13122358292将会和您联系。')
#         return jsonify({'Message': 'OK'})
#     except:
#         return jsonify({'Message': '我觉得不行'})

# @course.route('approve_of_professor', methods=['GET', 'POST'])
# @login_required
# def approve_of_professor():
#     try:
#         teacher =

@course.route('/cancel_professor/<int:id>', methods=['GET', 'POST'])
@login_required
def cancel_professor(id):
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=id).first_or_404()
    user.apply_message = 'r1ejected'
    db.session.add(user)
    flash(user.username + '删除成功')
    return redirect(url_for('.professor_manager', page=page))

@course.route('/professor_manager', methods=['POST', 'GET'])
@login_required
def professor_manager():
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get('page', 1, type=int)
    student = Role.query.filter_by(name='Student').first_or_404()
    professor_tobe = User.query.filter(User.role==student, User.teacher_date, User.apply_message!='r1ejected').order_by(User.teacher_date)
    pagination = professor_tobe.paginate(page, per_page=20, error_out=False)
    professors = pagination.items
    approve_form = ApproveForm()
    if approve_form.validate_on_submit():
        user = User.query.filter_by(username=approve_form.username.data).first_or_404()
        teacher = Role.query.filter_by(name='Teacher').first_or_404()
        subject = Subject.query.filter_by(subjectname=approve_form.subject.data).first_or_404()
        user.role = teacher
        user.subject = subject
        user.collegename = subject.school.collegename
        db.session.add(user)
        flash(user.username + '添加成功，专业' + subject.subjectname + '，学校' + user.collegename)
        return redirect(url_for('.professor_manager', page=page))
    return render_template('course/professor_manage.html', professors=professors, pagination=pagination,
                           form = approve_form)
