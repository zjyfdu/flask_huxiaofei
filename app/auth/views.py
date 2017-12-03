#coding: utf-8
from flask import render_template, redirect, request, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from ..lib.send_sms import send_sms
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, PhoneRegistrationForm
from PIL import Image
from werkzeug import secure_filename
import os


# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.ping()
#         if not current_user.confirmed \
#                 and request.endpoint \
#                 and request.endpoint[:5] != 'auth.' \
#                 and request.endpoint != 'static':
#             return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('course.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user is None:
            user = User.query.filter_by(cellphone=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('course.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('course.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/sendsms')
def sendsms():
    cellphone = request.args.get('cellphone', '')
    try:
        code = int(cellphone)
    except:
        return jsonify({'Message': "手机号不对啊"})
    if not(13000000000<code<19999999999):
        return jsonify({'Message': "手机号不对啊"})
    code = str(code % 1048577)[:6]
    message = send_sms(phone_numbers=str(cellphone), code=code)
    return jsonify(eval(message))

@auth.route('/registersms', methods=['GET', 'POST'])
def registersms():
    form = PhoneRegistrationForm()
    if form.validate_on_submit():
        user = User(cellphone=form.cellphone.data,
                    username=form.username.data,
                    password=form.password.data,
                    confirmed=True)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/registersms.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('course.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('course.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('course.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('course.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('course.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(cellphone=form.cellphone.data).first()
        if user:
            user.password = form.password.data
            db.session.add(user)
            flash(u'密码已重置，请重新登陆')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


# @auth.route('/change-email', methods=['GET', 'POST'])
# @login_required
# def change_email_request():
#     form = ChangeEmailForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.password.data):
#             new_email = form.email.data
#             token = current_user.generate_email_change_token(new_email)
#             send_email(new_email, 'Confirm your email address',
#                        'auth/email/change_email',
#                        user=current_user, token=token)
#             flash('An email with instructions to confirm your new email '
#                   'address has been sent to you.')
#             return redirect(url_for('course.index'))
#         else:
#             flash('Invalid email or password.')
#     return render_template("auth/change_email.html", form=form)
#
#
# @auth.route('/change-email/<token>')
# @login_required
# def change_email(token):
#     if current_user.change_email(token):
#         flash('Your email address has been updated.')
#     else:
#         flash('Invalid request.')
#     return redirect(url_for('course.index'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@auth.route('/edit-avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    if request.method == 'POST':
        file = request.files['file']
        size = (256, 256)
        im = Image.open(file)
        im.thumbnail(size)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            im.save(os.path.join(current_app.static_folder, 'avatar', filename))
            current_user.avatar_url = url_for('static', filename='%s/%s' % ('avatar', filename))
            db.session.add(current_user)
            flash(u'头像修改成功')
            return redirect(url_for('main.user', username=current_user.username))
    return render_template('auth/change_avatar.html')