from django.urls import path
from . import views
urlpatterns = [
# 判断用户名是否重复注册:GET /usernames/itcast/count/
    # path('usernames/itcast/count/', views.UsernameCountView.as_view()),
    # path('usernames/<'匹配用户名的路由转换器:变量'>/count/', views.UsernameCountView.as_view()),
# http://www.meiduo.site:8000/usernames/itcast/count/
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view()),
# /mobiles/(?P<mobile>1[3-9]\d{9})/count/
    path('mobiles/<mobile:mobile>/count/',views.MobileCountView.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('login/',views.LoginView.as_view()),
    path('logout/',views.LogoutView.as_view()),
    path('info/',views.UserInfoView.as_view()),
    path('emails/',views.EmailView.as_view()),
    path('emails/verification/',views.verifyEmailView.as_view()),
    path('addresses/create/',views.CreateAddressView.as_view()),
    path('addresses/',views.AddressView.as_view()),
    path('addresses/<int:address_id>/',views.UpdateDestroyAddressView.as_view()),
    path('addresses/<int:address_id>/default/',views.UpdateDefaultAddressView.as_view()),
    path('addresses/<int:address_id>/title/',views.UpdateTitleView.as_view()),
    path('password/',views.UpdatePasswordView.as_view()),

]