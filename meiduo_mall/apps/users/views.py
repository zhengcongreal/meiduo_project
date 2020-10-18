from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

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