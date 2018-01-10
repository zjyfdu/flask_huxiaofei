from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_login import LoginManager
from flask_msearch import Search
from config import config
from jieba.analyse import ChineseAnalyzer

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# db = SQLAlchemy()
search = Search(analyzer=ChineseAnalyzer())

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.app = app

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    search.init_app(app)

    from .alipay import alipay as alipay_blueprint
    app.register_blueprint(alipay_blueprint, url_prefix='/alipay')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/community')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .course import course as course_blueprint
    app.register_blueprint(course_blueprint)

    return app


from models import *
