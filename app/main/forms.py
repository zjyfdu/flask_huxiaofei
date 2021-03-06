# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField
from wtforms.validators import Length, Regexp, DataRequired
from wtforms import ValidationError
from ..models import Role, User, Topic

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired("内容不能为空")])
    topic = SelectField('话题', coerce=int)
    body = TextAreaField("内容", validators=[DataRequired("内容不能为空")])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.topic.choices = [(topic.id, topic.name)
                             for topic in Topic.query.order_by(Topic.name).all()]
        self.topic.choices.append((0, '无'))


class CommentForm(FlaskForm):
    parent_id = IntegerField("")
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('提交')

class ProfessorForm(FlaskForm):
    apply_message = StringField('申请信息')
    submit = SubmitField('提交')