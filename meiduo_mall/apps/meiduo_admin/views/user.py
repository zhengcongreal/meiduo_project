from rest_framework.generics import ListCreateAPIView
from apps.meiduo_admin.serializers.user import UserSerializers
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User
class UserListView(ListCreateAPIView):
    serializer_class = UserSerializers
    pagination_class  = PageNum
    def get_queryset(self):
        # 获取前端传递的keyword值
        keyworld=self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyworld is '' or keyworld is None:
            return User.objects.all()
        else:
            return User.objects.filter(username__contains=keyworld)


