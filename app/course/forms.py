# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, NumberRange, DataRequired, InputRequired
from wtforms import ValidationError
from ..models import User

class CourseForm(FlaskForm):
    title = StringField('课程名', validators=[DataRequired('内容不能为空')])
    price = IntegerField('价格', validators=[InputRequired("请填个自然数")])
    school = SelectField("选择学校", choices=[('chengdian', '成电'), ('fudan', '复旦'), ('dongnan', '东南'), ('zhongkeyuan', '中科院')])
    mode = SelectField("上课方式", choices=[('视频', '视频'), ('直播', '直播'), ('面对面', '面对面')])
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

class CourseFormAdmin(CourseForm):
    teachers = StringField('老师用户名，用空格隔开')
    submit = SubmitField('提交')

class SchoolFormAdmin(FlaskForm):
    introduction = TextAreaField("考试大纲", validators=[DataRequired('你家的考试大纲是空的？！')])
    introduction2 = TextAreaField("课程资料", validators=[DataRequired('你一定有资料的')])
    image = FileField('可以上传个背景图啊')
    submit = SubmitField('提交')

class CourseCommentForm(FlaskForm):
    parent_id = IntegerField("")
    body = StringField("", validators=[DataRequired("评论不能空啊")])
    submit = SubmitField('提交')

class CoursePostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired("内容不能为空")])
    free = BooleanField("是否为试听课", validators=[DataRequired("请选择")], default=False)
    body = TextAreaField("内容", validators=[DataRequired("内容不能为空")])
    submit = SubmitField('提交')