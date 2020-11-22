from django.urls import path
from . import views

urlpatterns = [

    # 支付宝支付: GET /payment/(?P<order_id>\d+)/
    path('payment/<int:order_id>/', views.PaymentView.as_view()),
    # 处理支付成功的回调: PUT /payment/status/
    path('payment/status/', views.PaymentStatusView.as_view()),

]

