from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.admin import AdminSerializer
from apps.meiduo_admin.serializers.permission import GroupSerialzier
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User


class AdminView(ModelViewSet):
    serializer_class = AdminSerializer
    # 获取管理员用户
    queryset = User.objects.filter(is_staff=True)
    pagination_class = PageNum


class AdminSimpleAPIView(APIView):

    def get(self,request):
        pers = Group.objects.all()
        ser = GroupSerialzier(pers, many=True)
        return Response(ser.data)
