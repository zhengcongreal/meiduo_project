from django.urls import path
from apps.meiduo_admin import login
from apps.meiduo_admin.views import home, user, sku

urlpatterns = [
     path('authorizations/',login.admin_jwt_token),
     # 日活统计
     path('statistical/day_active/',home.UserDailyActiveCountView.as_view()),
     # 日下单统计
     path('statistical/day_orders/',home.UserDailyOrderCountView.as_view()),
     # 月增用户统计
     path('statistical/month_increment/',home.UserMonthCountView.as_view()),
     # 用户总量统计
     path('statistical/total_count/',home.UserTotalCountView.as_view()),
     # 日增用户统计
     path('statistical/day_increment/',home.UserDailyIncrementView.as_view()),
     # 查询用户
     path('users/',user.UserListView.as_view()),
     # 获取sku表id,name
     path('skus/simple/',sku.SKUView.as_view()),




]

from .views import image
from rest_framework.routers import DefaultRouter

#创建router实例
router = DefaultRouter()
#注册路由
router.register(r'skus/images',image.ImageView,basename='image')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls
