# -*- coding: utf-8 -*-
# author: zhaijinyuan
# date: 2017/9/23 下午1:47

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import uuid

from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid

def send_sms(phone_numbers, code, sign_name=u'用芯学', template_code='SMS_99205013'):
    REGION = "cn-hangzhou"
    ACCESS_KEY_ID = "LTAIMTruE5BVPAyw"
    ACCESS_KEY_SECRET = "qlVNMS0I1uMc2dyYWSXBT0BNB5DGYN"
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
    template_param = "{\"code\":\"%s\"}" % code
    business_id = uuid.uuid1()
    smsRequest = SendSmsRequest.SendSmsRequest()
    smsRequest.set_TemplateCode(template_code)
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)
    smsRequest.set_OutId(business_id)
    smsRequest.set_SignName(sign_name)
    smsRequest.set_PhoneNumbers(phone_numbers)
    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)
    return smsResponse

# send_sms('13122358292', '123456')