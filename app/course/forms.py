# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, NumberRange
from wtforms import ValidationError
from ..models import User

class CourseForm(FlaskForm):
    title = StringField('课程名', validators=[Required('内容不能为空')])
    price = IntegerField('价格', validators=[Required("请填个自然数")])
    mode = StringField('上课方式', validators=[Required("内容不能为空")])
    abstract = StringField('课程简介', validators=[Required('内容不能为空')])
    introduction = TextAreaField("课程的详细介绍", validators=[Required("内容不能为空")])
    image = FileField('可以给课程加个展示的图片')
    submit = SubmitField('提交')

    def validate_price(self, field):
        if field.data<0:
            raise ValidationError(u'不要赔钱啊')
        elif field.data>20000:
            raise ValidationError(u'这么凶')


# class LoginForm(FlaskForm):
#     email = StringField('Email', validators=[Required(), Length(1, 64),
#                                              Email()])
#     password = PasswordField('Password', validators=[Required()])
#     remember_me = BooleanField('Keep me logged in')
#     submit = SubmitField('Log In')
#
#
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[Required(), Length(1, 64),
#                                            Email()])
#     username = StringField('Username', validators=[
#         Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
#                                           'Usernames must have only letters, '
#                                           'numbers, dots or underscores')])
#     password = PasswordField('Password', validators=[
#         Required(), EqualTo('password2', message='Passwords must match.')])
#     password2 = PasswordField('Confirm password', validators=[Required()])
#     submit = SubmitField('Register')
#
#     def validate_email(self, field):
#         if User.query.filter_by(email=field.data).first():
#             raise ValidationError('Email already registered.')
#
#     def validate_username(self, field):
#         if User.query.filter_by(username=field.data).first():
#             raise ValidationError('Username already in use.')
#
#
# class ChangePasswordForm(FlaskForm):
#     old_password = PasswordField('Old password', validators=[Required()])
#     password = PasswordField('New password', validators=[
#         Required(), EqualTo('password2', message='Passwords must match')])
#     password2 = PasswordField('Confirm new password', validators=[Required()])
#     submit = SubmitField('Update Password')
#
#
# class PasswordResetRequestForm(FlaskForm):
#     email = StringField('Email', validators=[Required(), Length(1, 64),
#                                              Email()])
#     submit = SubmitField('Reset Password')
#
#
# class PasswordResetForm(FlaskForm):
#     email = StringField('Email', validators=[Required(), Length(1, 64),
#                                              Email()])
#     password = PasswordField('New Password', validators=[
#         Required(), EqualTo('password2', message='Passwords must match')])
#     password2 = PasswordField('Confirm password', validators=[Required()])
#     submit = SubmitField('Reset Password')
#
#     def validate_email(self, field):
#         if User.query.filter_by(email=field.data).first() is None:
#             raise ValidationError('Unknown email address.')
#
#
# class ChangeEmailForm(FlaskForm):
#     email = StringField('New Email', validators=[Required(), Length(1, 64),
#                                                  Email()])
#     password = PasswordField('Password', validators=[Required()])
#     submit = SubmitField('Update Email Address')
#
#     def validate_email(self, field):
#         if User.query.filter_by(email=field.data).first():
#             raise ValidationError('Email already registered.')
