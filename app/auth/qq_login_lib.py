# -*- coding: utf-8 -*-
# author: zhaijinyuan
# date: 2018/1/22 下午6:13
import json
import requests
from flask import Flask, redirect, url_for, request, jsonify, g, render_template
from SpliceURL import Splice

timeout = 5
verify = False
QQ_APP_ID = '101453353'
QQ_APP_KEY = '76ad86532039361e6c66ebdfab5ac3aa'


class ServerError(Exception):
    pass

def Get_Access_Token(code, callbackurl):
    ''' Authorization Code cannot repeat '''
    Get_Access_Token_Url = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "authorization_code", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "code": code, "state": "P.passport", "redirect_uri": callbackurl}).geturl
    access_token_data = requests.get(Get_Access_Token_Url, timeout=timeout, verify=verify).text

    try:
        data = Parse_Access_Token(access_token_data)
    except Exception,e:
        app.logger.error(e, exc_info=True)
        data = Callback_Returned_To_Dict(access_token_data)

    #Should returned right data, such as {'access_token': '79D493208A237BAB3C9AE93FAD2798CE', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
    if isinstance(data, dict):
        return data
    else:
        raise ServerError("Get Access Token Error with Authorization Code")

def Update_Access_Token(refresh_token):
    '''Update some required parameters for OAuth2.0 API calls'''
    Update_Access_Token_Url = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "refresh_token", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "refresh_token": refresh_token}).geturl
    access_token_data = requests.get(Update_Access_Token_Url, timeout=timeout, verify=verify).text

    try:
        data = Parse_Access_Token(access_token_data)
    except Exception,e:
        app.logger.error(e, exc_info=True)
        data = Callback_Returned_To_Dict(access_token_data)
    #returned data, such as {'access_token': '79D493208A237BAB3C9AE93FAD2798CE', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
    if isinstance(data, dict):
        return data
    else:
        raise

def Get_OpenID(access_token):
    Get_OpenID_Url = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/me", query={"access_token": access_token}).geturl
    openid_data = requests.get(Get_OpenID_Url, timeout=timeout, verify=verify).text

    #Should returned right data, such as {"client_id":"100581101","openid":"AF8AA7E0F77451736DD97FB796849024"}
    return Callback_Returned_To_Dict(openid_data)

def Get_User_Info(access_token, openid):
    Get_User_Info_Url = Splice(scheme="https", netloc="graph.qq.com", path="/user/get_user_info", query={"access_token": access_token, "oauth_consumer_key": QQ_APP_ID, "openid": openid}).geturl
    return requests.get(Get_User_Info_Url, timeout=timeout, verify=verify).json()

def Parse_Access_Token(x):
    ''' parse string, such as access_token=E8BF2BCAF63B7CE749796519F5C5D5EB&expires_in=7776000&refresh_token=30AF0BD336324575029492BD2D1E134B'''
    return dict( _.split('=') for _ in x.split('&') )

def Callback_Returned_To_Dict(x):
    '''OAuthResponse class can't parse the JSON data with content-type text/html and because of a rubbish api, we can't just tell flask-oauthlib to treat it as json.'''
    if x.find(b'callback') > -1:
        # the rubbish api (https://graph.qq.com/oauth2.0/authorize) is handled here as special case
        pos_lb = x.find(b'{')
        pos_rb = x.find(b'}')
        x = x[pos_lb:pos_rb + 1]

    try:
        if type(x) != str:  # Py3k
            x = x.decode('utf-8')
        return json.loads(x, encoding='utf-8')
    except:
        return x