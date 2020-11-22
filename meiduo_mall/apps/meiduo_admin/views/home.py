from datetime import date, timedelta

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User


class UserDailyActiveCountView(APIView):
    '''
    日活用户统计
    '''
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取活跃用户总数
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            'count': count,
            'date': now_date
        })


class UserDailyOrderCountView(APIView):
    '''
    日下单用户量统计
    '''

    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取当日下单用户数量  orders__create_time 订单创建时间
        count = User.objects.filter(orderinfo__create_time__gte=now_date).count()
        return Response({
            "count": count,
            "date": now_date
        })


class UserMonthCountView(APIView):
    '''
    月增用户统计
    '''
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取30天之前的日期
        before_date = now_date - timedelta(days=30)
        date_list = []
        for i in range(30):
            start_date = before_date + timedelta(days=i)
            end_date = before_date + timedelta(days=i + 1)
            count = User.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date).count()
            date_list.append({'count': count, 'date': start_date})
        return Response(date_list)


class UserTotalCountView(APIView):
    '''用户总量统计'''
    def get(self,request):
        now_date=date.today()
        count=User.objects.all().count()
        return Response({'date':now_date,'count':count})



class UserDailyIncrementView(APIView):
    '''日增用户统计'''
    def get(self,request):
        now_date=date.today()
        count=User.objects.filter(date_joined__gte=now_date).count()
        return Response({'date':now_date,'count':count})
