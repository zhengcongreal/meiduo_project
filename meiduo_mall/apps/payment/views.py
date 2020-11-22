from django.shortcuts import render
from django.views import View
from django import http
from alipay import AliPay
from django.conf import settings
import os

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from apps.orders.models import OrderInfo
from apps.payment.models import Payment


# Create your views here.


class PaymentStatusView(LoginRequiredJSONMixin, View):
    """处理支付成功的回调
    PUT /payment/status/
    """

    def put(self, request):
        """保存支付结果"""
        # 接受参数：支付宝回调地址中的查询字符串参数
        query_dict = request.GET

        # 使用参数验证该回调是否是支付宝的回调
        # 将查询字符串参数转字典
        data_dict = query_dict.dict()
        # 再从参数字典中剔除并获取sign参数
        signature = data_dict.pop("sign")

        # 创建AliPay的SDK对象
        # 如果是安装的最新的支付宝SDK，读取秘钥的方式是读取秘钥字符串
        app_private_key_string_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "keys/app_private_key.pem")
        app_public_key_string_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "keys/alipay_public_key.pem")


        app_private_key_string = open(app_private_key_string_path, 'rb').read()
        alipay_public_key_string = open(app_public_key_string_path, 'rb').read()

        # 对接支付宝的支付接口
        # 创建AliPay的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用的ID，如果对接的是沙箱应用，那么就是沙箱应用的ID。反之，就是正式应用的ID
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 最后sign参数和其他查询字符串签名后的结果进行对比
        success = alipay.verify(data_dict, signature)
        if success:
            # 说明该回调是支付宝发送的安全回调
            # 读取支付宝和美多商城维护的订单号，并且绑定到一起
            out_trade_no = data_dict.get('out_trade_no')  # 美多订单号
            trade_no = data_dict.get('trade_no')  # 支付宝订单号
            Payment.objects.create(
                order_id=out_trade_no,
                trade_id=trade_no
            )

            # 修改订单的状态
            # order = OrderInfo.objects.get(order_id=out_trade_no, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
            # order.status = OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT']
            # order.save()

            OrderInfo.objects.filter(order_id=out_trade_no, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            # 响应结果
            return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'trade_id': trade_no})
        else:
            # 非法请求
            return http.JsonResponse({'code': 400, 'errmsg': '非法请求'})


class PaymentView(LoginRequiredJSONMixin, View):
    """支付宝支付
    GET /payment/(?P<order_id>\d+)/
    """

    def get(self, request, order_id):
        """
        对接支付宝的支付接口
        :param order_id: 要支付的订单号
        :return: 支付宝收银台扫码登录链接
        """
        # 校验order_id是否存在
        try:
            # 要去支付的订单必须订单编号存在，而且必须是当前登录用户本人的订单，而且订单的状态必须是待支付
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.JsonResponse({'code': 400, 'errmsg': '参数order_id错误'})


        # 如果是安装的最新的支付宝SDK，读取秘钥的方式是读取秘钥字符串
        app_private_key_string_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")
        app_public_key_string_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"keys/alipay_public_key.pem")

        app_private_key_string = open(app_private_key_string_path,'rb').read()
        alipay_public_key_string = open(app_public_key_string_path,'rb').read()



        # 对接支付宝的支付接口
        # 创建AliPay的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用的ID，如果对接的是沙箱应用，那么就是沙箱应用的ID。反之，就是正式应用的ID
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 使用AliPay的SDK对象调用支付的接口函数接口，得到收银台扫码登录路径order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 美多商城维护的订单号
            total_amount=str(order.total_amount),  # 实付款
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功后的回调地址
        )

        # 电脑网站支付，沙箱应用，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        # 电脑网站支付，正式应用，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        # 响应结果
        return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'alipay_url': alipay_url})