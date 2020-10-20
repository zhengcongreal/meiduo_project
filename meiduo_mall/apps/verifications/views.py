# Create your views here.
import random

from django import http
from django.views import View
from django.http import HttpResponse
from django_redis import get_redis_connection

from apps.verifications.libs.captcha import captcha
from apps.verifications.libs.yuntongxun.ccp_sms import CCP
import logging
logger=logging.getLogger('django')

class ImageCodeView(View):
    '''返回图形验证码的类视图'''

    def get(self, request, uuid):
        '''
        生成图形验证码, 保存到redis中, 另外返回图片
        :param request:请求对象
        :param uuid:浏览器端生成的唯一id
        :return:一个图片
        '''
        # 1.调用工具类 captcha 生成图形验证码
        text, image = captcha.captcha.generate_captcha()

        # 2.链接 redis, 获取链接对象
        redis_conn = get_redis_connection('verify_code')

        # 3.利用链接对象, 保存数据到 redis, 使用 setex 函数
        # redis_conn.setex('<key>', '<expire>', '<value>')
        redis_conn.setex('img_%s' % uuid, 60, text)

        # 4.返回(图片)
        return HttpResponse(image,
                            content_type='image/jpg')

class SMSCodeView(View):
    def get(self,request,mobile):
        # 往redis中存入数据, key值和value值随意指定, 但是时间必须为60s
        # 例如这里key:value为:  send_flag_mobile:1  时间为 60
        # 1. 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')
        send_flag_mobile=redis_conn.get('send_flag_%s'%mobile)
        if send_flag_mobile:
            return http.JsonResponse({'code':'400','errmsg':'发送短信频率太快了，亲稍后再试！'})


    # 2. 接收参数
        image_code_client  = request.GET.get("image_code")
        uuid=request.GET.get("image_code_id")
    # 3. 校验参数
        if not all([image_code_client,uuid]):
            return http.JsonResponse({'code':'400','errmsg':'缺少必传参数！'})


    # 4. 提取图形验证码
        image_code_server=redis_conn.get('img_%s'%uuid)
    # 图形验证码过期或者不存在
        if not image_code_server:
            return http.JsonResponse({'code':'400','errmsg':'图形验证码失效,请点击图形验证码刷新！'})
    # 5. 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)
    # 6. 对比图形验证码
    # bytes 转字符串
        image_code_server=image_code_server.decode()

    # 转小写后比较
        if image_code_client.lower()!=image_code_server.lower():
            return http.JsonResponse({'code':'400','errmsg':'图形验证码输入有误！'})

    # 7. 生成短信验证码：生成6位数验证码
        random_num=random.randint(0,999999)
    # 8. 保存短信验证码
        sms_code=("%06d"%random_num)
        logger.info(sms_code)

        # 创建 Redis 管道
        pl=redis_conn.pipeline()
        # 短信验证码有效期，单位：300秒
        pl.setex('sms_%s'%mobile,300,sms_code)
        pl.setex('send_flag_%s'%mobile,60,1)

        # 执行请求, 这一步千万别忘了
        pl.execute()
    #     redis_conn.setex('sms_%s'%mobile,300,sms_code)
        # 往 redis 中写入一个数据, 写入什么不重要, 时间重要
        # 我们给写入的数据设置为60s,如果过期,则会获取不到.
        # redis_conn.setex('send_flag_%s'%mobile,60,1)
    # 9. 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

    # 短信模板
    # 10. 响应结果
        return http.JsonResponse({'code':'0','errmsg':'短信发送成功！'})