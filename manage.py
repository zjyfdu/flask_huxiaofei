#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from app import create_app, db, search
from app.models import User, Follow, Role, Permission, Post, Comment, Course, School, CourseComment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import multiprocessing, time

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

@manager.command
def renewdb():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    User.fuck_me()
    School.insert_schools()

@manager.command
def update_index():
    while True:
        time.sleep(600)
        search.update_index()

def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow, Role=Role,
                School=School, CourseComment=CourseComment,
                Permission=Permission, Post=Post, Comment=Comment, Course=Course)
manager.add_command("shell", Shell(make_context=make_shell_context))

manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    p = multiprocessing.Process(target=update_index)
    p.start()
    manager.run()
