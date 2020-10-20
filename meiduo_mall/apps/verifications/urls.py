from django.urls import path

from . import views
urlpatterns = [
    # 图形验证码
    path('image_codes/<uuid:uuid>/', views.ImageCodeView.as_view()),
    # /sms_codes/(?P<mobile>1[3-9]\d{9})/
    path('sms_codes/<mobile:mobile>/',views.SMSCodeView.as_view())
]