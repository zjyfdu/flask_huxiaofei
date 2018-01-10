# -*- coding: utf-8 -*-
# author: zhaijinyuan
# date: 2018/1/9 下午8:50

from flask import render_template, redirect, request, url_for, flash, jsonify, current_app, make_response
from alipaylib import getOrderId, place_order, query_order
from flask_login import login_required
from . import alipay

@alipay.route("/create_order")
@login_required
def create_order():
    mon = request.args.get("mon")
    des = request.args.get("des")
    orderId = getOrderId()
    courseId = request.args.get("cou")
    if mon and des:
        create_order_url = place_order(orderId, float(mon), des, return_url=url_for('.callback', _external=True))
        query_order_url = query_order(orderId)
        response_dict = {'create_order_url': create_order_url,
                         'query_order_url': query_order_url,
                         'order_id': orderId,
                         'status': 'succeed'}
        resp = make_response(jsonify(response_dict))
        resp.set_cookie('order_id'+courseId, orderId, max_age=3600)
        resp.set_cookie('query_order_url'+courseId, query_order_url, max_age=3600)
        return resp
    return jsonify({'status': 'error'})

@alipay.route("/callback")
def callback():
    # if request.method=='POST':
    #     param=request.form.to_dict()
    # elif request.method=='GET':
    #     param=request.args.to_dict()
    # else:
    #     return "error"
    # re = notify_verify(param)
    # {'trade_no': u'2018010921001004580276368220', 'seller_id': u'2088122233733194', 'total_amount': u'1.00', 'timestamp': u'2018-01-09 20:15:55', 'charset': u'utf-8', 'app_id': u'2018010301557345', 'sign': u'mYJHx/P+BXfyu1dRrSZmgEnqXibjLnk/pSUuaaiIrvcGv6Dq9kJcw7GwXVWHB607cXMLWQ+BTUWrsB6umx88VBW5Db9P3xVl+iL1K+BtGCGgj5EQFwLG+VaWu3dwWvfK06apDdSKt01u+KKk02iu8qvicsWSsi3vTUcRTXtLw+IPvPUHCZSPTalNVooC5mpDSYhDJUES5hvibM5E/vMoYLXXH10YzIlH9mCCASF01Xj1pHgWaghC6thR+OKoR4Imdg+WSjZaPrMMhfXL1nSdYl1efZXHJsM/Trt/2WGjminp0BbLgwEnEyQPwhWZGIliL947jqKswkmkIsNQFXQTCg==', 'out_trade_no': u'201801092008018436598578', 'version': u'1.0', 'sign_type': u'RSA2', 'auth_app_id': u'2018010301557345', 'method': u'alipaylib.trade.page.pay.return'}
    return render_template('alipay/callback.html')