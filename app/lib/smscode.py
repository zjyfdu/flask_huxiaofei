# -*- coding: utf-8 -*-
# author: zhaijinyuan
# date: 2017/12/5 下午2:45

from datetime import datetime
import time

def generate_code(phonenum, bignum=1048577):
    utc_seconds = time.mktime(datetime.utcnow().timetuple())
    code = str((phonenum + utc_seconds) % bignum)[:6]
    return code

def verify_code(phonenum, code, time_delta=10, bignum=1048577):
    code_now = generate_code(phonenum, bignum)
    return (int(code_now)-int(code))<=time_delta

if __name__ == '__main__':
    code = generate_code(1)
    while True:
        time.sleep(1)
        print verify_code(1, code)