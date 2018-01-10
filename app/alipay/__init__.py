# -*- coding: utf-8 -*-
# author: zhaijinyuan
# date: 2018/1/9 下午8:50

from flask import Blueprint

alipay = Blueprint('alipay', __name__)

from . import views
