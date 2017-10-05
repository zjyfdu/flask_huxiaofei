#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, Comment, Course
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

@manager.command
def renewdb():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    User.fuck_me()

def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, Comment=Comment, Course=Course)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
