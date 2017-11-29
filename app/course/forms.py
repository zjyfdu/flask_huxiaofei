# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, NumberRange, DataRequired
from wtforms import ValidationError
from ..models import User

class CourseForm(FlaskForm):
    title = StringField('课程名', validators=[DataRequired('内容不能为空')])
    price = IntegerField('价格', validators=[DataRequired("请填个自然数")])
    mode = StringField('上课方式', validators=[DataRequired("内容不能为空")])
    abstract = StringField('课程简介', validators=[DataRequired('内容不能为空')])
    introduction = TextAreaField("课程的详细介绍", validators=[DataRequired("内容不能为空")])
    introduction2 = TextAreaField("加入课程之后展示", validators=[DataRequired("内容不能为空")])
    image = FileField('可以给课程加个展示的图片')
    submit = SubmitField('提交')

    def validate_price(self, field):
        if field.data<0:
            raise ValidationError(u'不要赔钱啊')
        elif field.data>20000:
            raise ValidationError(u'这么凶')


class SubjectForm(FlaskForm):
    title = StringField('专业课', validators=[DataRequired('内容不为空')])
    school = SelectField("选择学校", choices=[('chengdian', '成电'), ('fudan', '复旦'), ('dongnan', '东南'), ('zhongkeyuan', '中科院')])
    about_subject = TextAreaField('专业的详细点的介绍', validators=[DataRequired('内容不为空')])
    submit = SubmitField("提交")

class ApproveForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('内容不为空')])
    school = SelectField("选择学校", choices=[('chengdian', '成电'), ('fudan', '复旦'), ('dongnan', '东南'), ('zhongkeyuan', '中科院')])
    subject = StringField('专业课', validators=[DataRequired('内容不为空')])
    submit = SubmitField("提交")

    # def validate_subject(self, field):
    #     if field.data<0:
    #         raise ValidationError(u'不要赔钱啊')
    #     elif field.data>20000:
    #         raise ValidationError(u'这么凶')