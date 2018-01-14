#-*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import Length, Email, Regexp, EqualTo, NumberRange, DataRequired
from wtforms import ValidationError
from ..models import User
from flask import session
from time import time


class LoginForm(FlaskForm):
    email = StringField(u'用户名或手机号', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField('记住登陆')
    submit = SubmitField('立即登陆')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                           Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册，可找回密码。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被占用了。')

class PhoneRegistrationForm(FlaskForm):
    cellphone = IntegerField(u'手机号', validators=[DataRequired(), NumberRange(13000000000, 19999999999)])
    verificationcode = StringField(u'验证码', validators=[DataRequired(), Regexp('^\d{1,6}$')])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_cellphone(self, field):
        if User.query.filter_by(cellphone=field.data).first():
            raise ValidationError(u'手机号已被注册，可找回密码。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被占用了。')

    def validate_verificationcode(self, field):
        cellphone = str(self.cellphone.data)
        cell_code_time = session.get(cellphone, {})
        if not cell_code_time:
            raise ValidationError(u'请重新发送验证码。')
        cell_code_time = eval(cell_code_time)
        if cell_code_time['time'] + 300 < time():
            raise ValidationError(u'验证码过期,请重试。')
        if field.data!=cell_code_time['code']:
            raise ValidationError(u'验证码错误，请重试。')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('确定')


# class PasswordResetRequestForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Length(1, 64),
#                                              Email()])
#     submit = SubmitField('Reset Password')


class PasswordResetRequestForm(FlaskForm):
    cellphone = IntegerField(u'手机号', validators=[DataRequired(), NumberRange(13000000000, 19999999999)])
    verificationcode = StringField(u'验证码', validators=[DataRequired(), Regexp('^\d{1,6}$')])
    password = PasswordField(u'新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(u'确认新密码', validators=[DataRequired()])
    submit = SubmitField(u'确定')

    def validate_cellphone(self, field):
        if not User.query.filter_by(cellphone=field.data).first():
            raise ValidationError(u'手机号没有注册过，直接注册新账号。')

    def validate_verificationcode(self, field):
        cellphone = str(self.cellphone.data)
        cell_code_time = session.get(cellphone, {})
        if not cell_code_time:
            raise ValidationError(u'请重新发送验证码。')
        cell_code_time = eval(cell_code_time)
        if cell_code_time['time'] + 300 < time():
            raise ValidationError(u'验证码过期,请重试。')
        if field.data!=cell_code_time['code']:
            raise ValidationError(u'验证码错误，请重试。')

class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
