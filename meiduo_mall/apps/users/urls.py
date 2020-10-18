from django.urls import path
from . import views
urlpatterns = [
# 判断用户名是否重复注册:GET /usernames/itcast/count/
    # path('usernames/itcast/count/', views.UsernameCountView.as_view()),
    # path('usernames/<'匹配用户名的路由转换器:变量'>/count/', views.UsernameCountView.as_view()),
# http://www.meiduo.site:8000/usernames/itcast/count/
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view())

]