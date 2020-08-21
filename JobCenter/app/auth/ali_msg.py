#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
# 连接阿里云
client = AcsClient('LTAI4G6m4kFpz4EAdcMyk8Bz', 'k8FxkuKjOCwNV3d362T5G3muIrFedE', 'cn-hangzhou')

def aliyun_sms_send(code):
   # 构建请求
   request = CommonRequest()
   request.set_accept_format('json')
   request.set_domain('dysmsapi.aliyuncs.com')
   request.set_method('POST')
   request.set_protocol_type('https') # https | http
   request.set_version('2017-05-25')
   request.set_action_name('SendSms')

   sms_code = code

   # 自定义参数
   request.add_query_param('RegionId', "cn-hangzhou")
   request.add_query_param('PhoneNumbers', "18506243060")
   request.add_query_param('SignName', "定时任务")
   request.add_query_param('TemplateCode', "SMS_200177064")
   request.add_query_param('TemplateParam', json.dumps({'code': code}))

   response = client.do_action(request)
   # python2:  print(response)
   print(str(response, encoding = 'utf-8'))

sms_send = aliyun_sms_send()