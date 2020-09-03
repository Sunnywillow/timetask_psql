#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import os

# 连接阿里云
ACCESS_KEY_APPID = os.environ.get('ACCESS_KEY_APPID')
ACCESS_KEY_SECRET = os.environ.get('ACCESS_KEY_SECRET')
ADMIN_PHOME_NUMBER = os.environ.get('ADMIN_PHOME_NUMBER')

client = AcsClient(ACCESS_KEY_APPID, ACCESS_KEY_SECRET, 'cn-hangzhou')


def aliyun_sms_send(code):
   # 构建请求
   request = CommonRequest()
   request.set_accept_format('json')
   request.set_domain('dysmsapi.aliyuncs.com')
   request.set_method('POST')
   request.set_protocol_type('https') # https | http
   request.set_version('2017-05-25')
   request.set_action_name('SendSms')


   # 自定义参数
   request.add_query_param('RegionId', "cn-hangzhou")
   request.add_query_param('PhoneNumbers', ADMIN_PHOME_NUMBER)
   request.add_query_param('SignName', "定时任务")
   request.add_query_param('TemplateCode', "SMS_200177064")
   request.add_query_param('TemplateParam', json.dumps({'code': code}))
   response = client.do_action(request)
   response_str = str(response, encoding='utf-8')

   # python2:  print(response)
   print(str(response_str))
   statusCode = json.loads(response_str).get('Code')

   print("Code: %s" %statusCode)
   if statusCode == 'OK':
      # 发送成功
      return 0
   else:
      # 发送失败
      return -1

# sms_send = aliyun_sms_send(18506243060)