import json
import re

from django import http
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User
import logging
logger=logging.getLogger('django')

class UsernameCountView(View):
    def get(self,request,username):
        '''判断用户名是否重复'''
        # 1.查询username在数据库中的个数
        try:
            count=User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':400,"errmsg":'访问数据库失败！'})

        return JsonResponse({'code':200,'errmsg':'ok','count':count})

class MobileCountView(View):
    def get(self,request,mobile):
        try:
            count=User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logging.error(e)
            return JsonResponse({'code':'400','errmsg':'访问数据库失败'})
        return JsonResponse({'code':'200','errmsg':'ok','count':count})


class RegisterView(View):
    def post(self,request):
        '''接收参数, 保存到数据库'''
        # 1.接收参数
        mydict=json.loads(request.body.decode())
        username=mydict.get('username')
        password=mydict.get('password')
        password2=mydict.get('password2')
        mobile=mydict.get('mobile')
        allow=mydict.get('allow')
        sms_code_client=mydict.get('sms_code')

        # 2.校验(整体)
        if not all([username,password,password2,mobile,allow]):
            return JsonResponse({'code':'400','errmsg':'缺少必传参数！'})

            # 3.username检验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400,
                                          'errmsg': 'username格式有误'})

            # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                          'errmsg': 'password格式有误'})

            #5.password2和password1
        if password !=password2:
            return JsonResponse({'code':'400','errmsg':'两次密码输入有误！'})

            # 6.mobile检验
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': 'moblie格式有误'})
            # 7 allow检验
        if allow !=True:
            return JsonResponse({'code': 400,
                                 'errmsg': 'allow格式有误'})
            # 8.sms_code检验 (链接redis数据库)
        redis_conn=get_redis_connection('verify_code')
            # 9.从redis中取值
        sms_code_server=redis_conn.get('sms_%s'%mobile)

        # 10.判断该值是否存在

        if not sms_code_server:
            return JsonResponse({'code':'400','errmsg':'短信验证码过期'})

        # 11.把redis中取得值和前端发的值对比
        if sms_code_server.decode()!=sms_code_client:
            return JsonResponse({'code':'400','errmsg':'短信验证码输入有误！'})
        # 12.保存到数据库 (username password mobile)
        try:
            user=User.objects.create_user(username=username,password=password,mobile=mobile)
        except Exception as e:
            logging.error(e)
            return JsonResponse({'code': '400', 'errmsg': '访问数据库失败'})

        # 添加如下代码
        # 实现状态保持
        login(request,user)

        return JsonResponse({'code': '0', 'errmsg': 'ok'})