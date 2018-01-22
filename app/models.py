#coding: utf-8
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADD_CLASS = 0x10
    MANAGE_TEACHER = 0x40
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Student': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Teacher': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.ADD_CLASS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

registrations = db.Table('registrations',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                         )
registrationst = db.Table('registrationst',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                         )

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __searchable__ = ['username', 'name', 'about_me']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    cellphone = db.Column(db.Integer, unique=True, index=True)
    qq_openid = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    collegename = db.Column(db.String(32))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    avatar_url = db.Column(db.String(128))
    teacher_date = db.Column(db.DateTime()) #申请成为老师的时间
    apply_message = db.Column(db.String(128)) #申请成为老师的信息
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    coursecomments = db.relationship('CourseComment', backref='user', lazy='dynamic')
    studentscourses = db.relationship('Course',
                                      secondary=registrations,
                                      backref=db.backref('students', lazy='dynamic'),
                                      lazy='dynamic')
    teachercourses = db.relationship('Course',
                                      secondary=registrationst,
                                      backref=db.backref('teachers', lazy='dynamic'),
                                      lazy='dynamic')

    @staticmethod
    def generate_me():
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime
        admin = Role.query.filter_by(name='Administrator').first()
        student = Role.query.filter_by(name='Student').first()
        u = User.query.filter_by(username='admin').first()
        if u:
            db.session.delete(u)
            db.session.commit()
        u = User(cellphone='13122358292',
             username='admin',
             password='yongxinxue',
             confirmed=True,
             name='admin',
             location='shanghai',
             about_me='admin user',
             collegename='chengdian',
             member_since=datetime.now(),
             role=admin)
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        u = User.query.filter_by(username='teacher').first()
        if u:
            db.session.delete(u)
            db.session.commit()
        s = User(cellphone='13122358291',
             username='teacher',
             password='yongxinxue',
             confirmed=True,
             name='teacher',
             location='shanghai',
             about_me='teacher account',
             collegename='chengdian',
             member_since=datetime.now(),
             role=student)
        db.session.add(s)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        teacher = Role.query.filter_by(name='Student').first()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     cellphone=forgery_py.address.phone(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True),
                     role=teacher,
                     teacher_date=forgery_py.date.date(True),
                     apply_message=forgery_py.lorem_ipsum.sentence())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
        if self.username is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.username.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))
        self.avatar_url = self.gravatar(size=280)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # def generate_reset_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'reset': self.id})

    # def reset_password(self, token, new_password):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('reset') != self.id:
    #         return False
    #     self.password = new_password
    #     db.session.add(self)
    #     return True

    # def generate_email_change_token(self, new_email, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'change_email': self.id, 'new_email': new_email})
    #
    # def change_email(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('change_email') != self.id:
    #         return False
    #     new_email = data.get('new_email')
    #     if new_email is None:
    #         return False
    #     if self.query.filter_by(email=new_email).first() is not None:
    #         return False
    #     self.email = new_email
    #     db.session.add(self)
    #     return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.username.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username



class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post', backref='topic', lazy='dynamic')

    @staticmethod
    def insert_topics():
        topics = [u'复旦', u'成电', u'东南', u'中科院']
        for t in topics:
            topic = Topic.query.filter_by(name=t).first()
            if topic is None:
                topic = Topic(name=t)
            db.session.add(topic)
        db.session.commit()

    def __repr__(self):
        return '<Topic %r>' % self.name


class Post(db.Model):
    """
    有普通post和课程post两种，通过belongtocourse区分
    """
    __tablename__ = 'posts'
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id')) #普通post的
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id')) #课程post的
    belong_to_course = db.Column(db.Boolean, default=False) #是否为课程的post
    course_free = db.Column(db.Boolean, default=False) #课程是否免费

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

class Comment(db.Model):
    """
    post comment
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('children'))
    childrencount = db.Column(db.Integer, default=0)

    @staticmethod
    def on_changed_parent_id(target, value, oldvalue, initiator):
        current = Comment.query.filter_by(id=value).first()
        while current:
            current.childrencount += 1
            db.session.add(current)
            db.session.commit()
            current = current.parent

db.event.listen(Comment.parent_id, 'set', Comment.on_changed_parent_id)

class Course(db.Model):
    __tablename__ = 'courses'
    __searchable__ = ['title', 'abstract', 'introduction']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    abstract = db.Column(db.String(256))
    introduction = db.Column(db.Text)
    introduction2 = db.Column(db.Text) #付款之后能看到的界面
    price = db.Column(db.Float)
    mode = db.Column(db.String(32))
    img_url = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    coursecomments = db.relationship('CourseComment', backref='course', lazy='dynamic')
    courseposts = db.relationship('Post', backref='course', lazy='dynamic')


    def __repr__(self):
        return '<Course %r>' % self.title

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(abstract=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     price=randint(0, 1000),
                     mode='视频直播',
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

class CourseComment(db.Model):
    __tablename__ = 'coursecomment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('coursecomment.id'))
    parent = db.relationship('CourseComment', remote_side=[id], backref=db.backref('children'))
    childrencount = db.Column(db.Integer, default=0)

    @staticmethod
    def on_changed_parent_id(target, value, oldvalue, initiator):
        current = CourseComment.query.filter_by(id=value).first()
        while current:
            current.childrencount += 1
            db.session.add(current)
            db.session.commit()
            current = current.parent

db.event.listen(CourseComment.parent_id, 'set', CourseComment.on_changed_parent_id)

class School(db.Model):
    __tablename__ = 'school'
    __searchable__ = ['collegename', 'actualname', 'introduction', 'introduction2']
    id = db.Column(db.Integer, primary_key=True)
    collegename = db.Column(db.String(32), unique=True)
    actualname = db.Column(db.String(64))
    courses = db.relationship('Course', backref='school', lazy='dynamic')
    introduction = db.Column(db.Text)
    introduction2 = db.Column(db.Text)
    img_url = db.Column(db.String(256))

    def __repr__(self):
        return '<School %r>' % self.collegename

    @staticmethod
    def insert_schools():
        schools = [('chengdian', u'电子科技大学,成都电子科技大学,成电'),
                   ('fudan', u'复旦大学'),
                   ('dongnan', u'东南大学,东大'),
                   ('zhongkeyuan', u'中国科学院大学微电子所,中科院微电子所')]
        for s in schools:
            # school = School.query.filter_by(collegename=s).first()
            # if school is None:
            school = School(collegename=s[0],
                            actualname=s[1])
            db.session.add(school)
        db.session.commit()