from django.contrib.auth.models import Permission
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.utils import PageNum
from apps.meiduo_admin.serializers.permission import PermissionSerialzier, GroupSerialzier
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import ContentType
from apps.meiduo_admin.serializers.permission import ContentTypeSerialzier
from django.contrib.auth.models import Group

from django.contrib.auth.models import Permission

class PermissionView(ModelViewSet):
    serializer_class = PermissionSerialzier
    queryset = Permission.objects.all()
    pagination_class = PageNum



class ContentTypeAPIView(APIView):

    def get(self,request):
        # 查询全选分类
        content = ContentType.objects.all()
        # 返回结果
        ser = ContentTypeSerialzier(content, many=True)

        return Response(ser.data)



class GroupView(ModelViewSet):
    serializer_class = GroupSerialzier
    queryset = Group.objects.all()
    pagination_class = PageNum


class GroupSimpleAPIView(APIView):

    def get(self,request):
        pers = Permission.objects.all()
        ser = PermissionSerialzier(pers, many=True)  # 使用以前定义的全选序列化器
        return Response(ser.data)
