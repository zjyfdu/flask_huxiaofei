# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, current_app, abort
from . import course
from .. import db
from ..models import User, Course, Role, Permission, School, CourseComment, Post
from .forms import CourseForm, CourseFormAdmin, SchoolFormAdmin, CourseCommentForm, CoursePostForm
from PIL import Image
from flask_login import current_user, login_required
from datetime import datetime
import os

@course.route('/')
def index():
    return redirect(url_for('course.college', collegename='fudan'))

@course.route('/college/<string:collegename>', methods=['GET', 'POST'])
def college(collegename):
    school = School.query.filter_by(collegename=collegename).first_or_404()
    form = SchoolFormAdmin()
    if current_user.is_administrator() and form.validate_on_submit():
        school.introduction=form.introduction.data
        school.introduction2=form.introduction2.data
        file = request.files[form.image.name]
        if file:
            if school.img_url:
                try:
                    os.remove(os.path.join(current_app.static_folder, 'schoolbanner', os.path.split(school.img_url)[-1]))
                except:
                    pass
            size = (1140, 160)
            im = Image.open(file)
            im = im.resize(size)
            from ..main.views import gen_rnd_filename
            fname, fext = os.path.splitext(file.filename)
            rnd_name = '%s%s' % (gen_rnd_filename(), fext)
            im.save(os.path.join(current_app.static_folder, 'schoolbanner', rnd_name))
            school.img_url = url_for('static', filename='%s/%s' % ('schoolbanner', rnd_name))
        db.session.add(school)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('course.college', collegename=collegename))
    form.introduction.data = school.introduction
    form.introduction2.data = school.introduction2
    return render_template('course/college.html', school=school, form=form)

@course.route('/class/<int:id>', methods=['GET', 'POST'])
def classes(id):
    course = Course.query.get_or_404(id)
    form = CourseCommentForm()
    if form.validate_on_submit():
        if current_user.is_anonymous:
            return current_app.login_manager.unauthorized()
        coursecomment = CourseComment(user=current_user,
                                      course=course,
                                      body=form.body.data,
                                      parent_id=form.parent_id.data)
        db.session.add(coursecomment)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('course.classes', id=id))
    coursecomments = [comment for comment in course.coursecomments if not comment.parent]
    return render_template('course/class.html', course=course, form=form,
                           coursecomments=coursecomments)


@course.route('/addcourse', methods=['GET', 'POST'])
def addcourse():
    form = CourseFormAdmin() if current_user.can(Permission.ADMINISTER) else CourseForm()
    if not current_user.can(Permission.ADD_CLASS):
        abort(403)
    if form.validate_on_submit():
        school = School.query.filter_by(collegename=form.school.data).first_or_404()
        course = Course(title=form.title.data,
                        abstract=form.abstract.data,
                        introduction=form.introduction.data,
                        introduction2=form.introduction2.data,
                        price=form.price.data,
                        mode=form.mode.data,
                        school=school,
                        timestamp=datetime.now())
        file = request.files[form.image.name]
        if current_user.can(Permission.ADMINISTER):
            for teachername in form.teachers.data.split():
                teacher = User.query.filter_by(username=teachername).first()
                if teacher and teacher not in course.teachers:
                    course.teachers.append(teacher)
        else:
            course.teachers.append(current_user)
        if file:
            size = (240, 140)
            im = Image.open(file)
            im = im.resize(size)
            from ..main.views import gen_rnd_filename
            fname, fext = os.path.splitext(file.filename)
            rnd_name = '%s%s' % (gen_rnd_filename(), fext)
            im.save(os.path.join(current_app.static_folder, 'courseimg', rnd_name))
            course.img_url = url_for('static', filename='%s/%s' % ('courseimg', rnd_name))
        db.session.add(course)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('course.classes', id=course.id))
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
    if current_user not in course.teachers and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = CourseFormAdmin() if current_user.can(Permission.ADMINISTER) else CourseForm()
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
                try:
                    os.remove(os.path.join(current_app.static_folder, 'courseimg', os.path.split(course.img_url)[-1]))
                except:
                    pass
            size = (240, 140)
            im = Image.open(file)
            im = im.resize(size)
            from ..main.views import gen_rnd_filename
            fname, fext = os.path.splitext(file.filename)
            rnd_name = '%s%s' % (gen_rnd_filename(), fext)
            im.save(os.path.join(current_app.static_folder, 'courseimg', rnd_name))
            course.img_url = url_for('static', filename='%s/%s' % ('courseimg', rnd_name))
        if current_user.can(Permission.ADMINISTER):
            for teacher in course.teachers:
                course.teachers.remove(teacher)
            for teachername in form.teachers.data.split():
                teacher = User.query.filter_by(username=teachername).first()
                if teacher and teacher not in course.teachers:
                    course.teachers.append(teacher)
        else:
            course.teachers.append(current_user)
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
    if current_user.can(Permission.ADMINISTER):
        form.teachers.data = ' '.join([teacher.username for teacher in course.teachers])
    return render_template('course/editcourse.html', form=form)

@course.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
def removecourse(id):
    course = Course.query.get_or_404(id)
    if current_user not in course.teachers and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    db.session.delete(course)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    flash('课程已删除')
    return redirect(url_for('course.college', collegename=current_user.collegename))

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

@course.route('/add_professor/<int:id>', methods=['GET', 'POST'])
@login_required
def add_professor(id):
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=id).first_or_404()
    teacher = Role.query.filter_by(name='Teacher').first_or_404()
    user.role = teacher
    db.session.add(user)
    flash(user.username + '添加成功')
    return redirect(url_for('.professor_manager', page=page))

@course.route('/professor_manager', methods=['POST', 'GET'])
@login_required
def professor_manager():
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get('page', 1, type=int)
    professor_tobe = User.query.order_by(User.last_seen)
    pagination = professor_tobe.paginate(page, per_page=50, error_out=False)
    professors = pagination.items
    return render_template('course/professor_manage.html', professors=professors, pagination=pagination)

@course.route("/search")
def w_search():
    keyword = request.args.get('q')
    courses = Course.query.msearch(keyword, fields=['title', 'abstract', 'introduction'], or_=True).all()
    teacherrole = Role.query.filter_by(name='Teacher').first_or_404()
    teachers = User.query.filter_by(role=teacherrole).msearch(keyword, fields=['username', 'name', 'about_me'], or_=True).all()
    schools = School.query.msearch(keyword, fields=['collegename', 'actualname', 'introduction', 'introduction2'], or_=True).all()
    posts = Post.query.msearch(keyword, fields=['title', 'body'], or_=True).all()
    return render_template('course/search.html', teachers=teachers, courses=courses, schools=schools, posts=posts)

@course.route("/add_course_post/<int:id>", methods=['GET', 'POST'])
def add_course_post(id):
    form = CoursePostForm()
    course = Course.query.filter_by(id=id).first_or_404()
    if current_user not in course.teachers and not current_user.is_administrator():
        abort(403)
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    course_free=form.free.data,
                    author=current_user._get_current_object(),
                    course_id=id,
                    belong_to_course=True)
        db.session.add(post)
        return redirect(url_for('.classes', id=id))
    return render_template('main/add_post.html', form=form)

@course.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    course = post.course
    if not post.belong_to_course:
        return redirect(url_for('main.edit', id=id))
    if current_user not in course.teachers and not current_user.is_administrator():
        abort(403)
    form = CoursePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.course_free = form.free.data
        post.last_update = datetime.utcnow()
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=id))
    form.body.data = post.body
    form.title.data = post.title
    form.free.data = post.course_free
    return render_template('main/edit_post.html', form=form)

@course.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    course = post.course
    if not post.belong_to_course:
        return redirect(url_for('main.post', id=id))
    if not post.course_free \
            and current_user not in course.teachers \
            and not current_user.is_administrator():
        flash("请先加入该课程")
        return redirect(url_for('course.classes', id=post.course.id))
    # form = CommentForm()
    # if form.validate_on_submit():
    #     if current_user.is_anonymous:
    #         return current_app.login_manager.unauthorized()
    #     comment = Comment(body=form.body.data,
    #                       post=post,
    #                       author=current_user._get_current_object(),
    #                       parent_id=form.parent_id.data)
    #     db.session.add(comment)
    #     post.last_update = datetime.datetime.utcnow()
    #     db.session.add(post)
    #     return redirect(url_for('.post', id=post.id, page=-1))
    # comments = [comment for comment in post.comments if not comment.parent]
    return render_template('course/post.html', post=post)