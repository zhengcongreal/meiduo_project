import json
import re
from django import http
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse

# Create your views here.

from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User, Address
import logging

from apps.users.utils import generate_email_verify_url, check_email_verify_url
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')


class UsernameCountView(View):
    def get(self, request, username):
        '''判断用户名是否重复'''
        # 1.查询username在数据库中的个数
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, "errmsg": '访问数据库失败！'})

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class MobileCountView(View):
    '''判断手机号是否重复'''

    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logging.error(e)
            return JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class RegisterView(View):
    def post(self, request):
        '''实现注册接口'''
        # 1.接收参数
        mydict = json.loads(request.body.decode())
        username = mydict.get('username')
        password = mydict.get('password')
        password2 = mydict.get('password2')
        mobile = mydict.get('mobile')
        allow = mydict.get('allow')
        sms_code_client = mydict.get('sms_code')

        # 2.校验(整体)
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数！'})

            # 3.username检验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400,
                                 'errmsg': 'username格式有误'})

            # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'errmsg': 'password格式有误'})

            # 5.password2和password1
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码输入有误！'})

            # 6.mobile检验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': 'moblie格式有误'})
            # 7 allow检验
        if allow != True:
            return JsonResponse({'code': 400,
                                 'errmsg': 'allow格式有误'})
            # 8.sms_code检验 (链接redis数据库)
        redis_conn = get_redis_connection('verify_code')
        # 9.从redis中取值
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        # 10.判断该值是否存在

        if not sms_code_server:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})

        # 11.把redis中取得值和前端发的值对比
        if sms_code_server.decode() != sms_code_client:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码输入有误！'})
        # 12.保存到数据库 (username password mobile)
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logging.error(e)
            return JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})

        # 实现状态保持
        login(request, user)

        # 生成响应对象
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 设置cookie
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response


class LoginView(View):
    def post(self, request):
        '''实现登录接口'''
        # 1.接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')
        # 2.校验(整体 + 单个)
        if not all([username, password]):
            return JsonResponse({'code': '400', 'errmsg': '缺少必传参数！'})

        # 3.如果匹配到用户名是手机号格式的,修改类属性Usernamefiled为mobile
        if re.match(r'^1[3-9]\d{9}$', username):
            User.USERNAME_FIELD = "mobile"
        else:
            if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
                return JsonResponse({'code': 400, 'errmsg': 'username格式有误！'})
            User.USERNAME_FIELD = "username"

        # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'errmsg': 'password格式有误'})
        # 3.验证是否能够登录
        user = authenticate(username=username, password=password)

        # 判断是否为空,如果为空,返回
        if user is None:
            return JsonResponse({'code': 400,
                                 'errmsg': '用户名或密码错误！'})
        # 4.状态保持
        login(request, user)
        # 5.判断是否记住用户
        if remembered != True:
            # 7.如果没有记住: 关闭立刻失效
            request.session.set_expiry(0)
        # 6.如果记住:  设置为两周有效
        else:
            request.session.set_expiry(None)
        # 8.返回json
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 9.设置cookie
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response


class LogoutView(View):
    """定义退出登录的接口"""

    def delete(self, request):
        """实现退出登录逻辑"""
        # 清理 session
        logout(request)
        # 创建 response 对象.
        response = http.JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 清除cookie
        response.delete_cookie('username')
        return response


class UserInfoView(LoginRequiredJSONMixin, View):
    """用户中心"""

    def get(self, request):
        my_dict = {
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': request.user.username,
                'mobile': request.user.mobile,
                'email': request.user.email,
                'email_active': request.user.email_active
            }
        }

        return JsonResponse(my_dict)


class EmailView(View):
    """添加邮箱"""

    def put(self, request):
        """实现添加邮箱逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        if not email:
            return JsonResponse({'code': 400, 'errmsg':
                '缺少email'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '邮箱格式错误！'})

        try:
            # 赋值 email 字段
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '添加邮箱失败！'})

        # 生成邮箱验证链接
        verify_url = generate_email_verify_url(user=request.user)
        # 调用发送的函数:
        send_verify_email.delay(email, verify_url)
        # 响应添加邮箱结果
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class verifyEmailView(View):
    """验证邮箱"""

    def put(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数：判断 token 是否为空和过期，提取 user
        if not token:
            return JsonResponse({'code': 400, 'errmsg': '缺少token'})
        # 调用上面封装好的方法, 将 token 传入

        user = check_email_verify_url(token)
        if not user:
            return JsonResponse({'code': 400, 'errmsg': '无效的token'})
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '激活邮箱失败'})
        # 返回邮箱验证结果
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class CreateAddressView(View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""

        # 获取地址个数:
        try:
            # count = Address.objects.filter(user=request.user,
            #                                is_deleted=False).count()
            count=request.user.addresses.filter(is_deleted=False).count()
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '获取地址数据出错'})
            # 判断是否超过地址上限：最多20个
        if count >= 20:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '参数mobile有误'})

        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return http.JsonResponse({'code': 400,
        #                                   'errmsg': '参数tel有误'})
        # if email:
        #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #         return http.JsonResponse({'code': 400,
        #                                   'errmsg': '参数email有误'})
                # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400,
                                      'errmsg': '新增地址失败'})

            # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': 0,
                                  'errmsg': '新增地址成功',
                                  'address': address_dict})

class AddressView(View):
    """用户收货地址"""

    def get(self, request):
        """提供地址管理界面
        """
        # 获取所有的地址:
        # addresses = Address.objects.filter(user=request.user,
        #                                    is_deleted=False)
        addresses=request.user.addresses.filter(is_deleted=False)
        # 创建空的列表
        address_dict_list = []
        # 遍历
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }

            # 将默认地址移动到最前面
            default_address = request.user.default_address
            if default_address.id == address.id:
                  # 查询集 addresses 没有 insert 方法
                address_dict_list.insert(0, address_dict)
            else:
                address_dict_list.append(address_dict)


        default_id = request.user.default_address_id

        return http.JsonResponse({'code':0,
                                  'errmsg':'ok',
                                  'addresses':address_dict_list,
                                  'default_address_id':default_id})


class UpdateDestroyAddressView(View):
    """用户收货地址修改和删除"""
    def put(self,request,address_id):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '参数mobile有误'})

        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return http.JsonResponse({'code': 400,
        #                                   'errmsg': '参数tel有误'})
        # if email:
        #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #         return http.JsonResponse({'code': 400,
        #                                   'errmsg': '参数email有误'})
        # 保存地址信息

        try:
            Address.objects.filter(id=address_id).update(
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

        except Exception as e:

            logger.error(e)
            return JsonResponse({'code':400,'errmsg':'更新出错了！'})
        else:
            address=Address.objects.get(id=address_id)
            address_dict = {
                "id":address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
        return JsonResponse({'code': 0, 'errmsg': 'ok','address':address_dict})

    def delete(self,request,address_id):

        try:
            address=Address.objects.get(id=address_id)
            address.is_deleted=True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '删除失败'})
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class UpdateDefaultAddressView(View):
    '''修改默认地址'''
    def put(self,request,address_id):
        try:
            address=Address.objects.get(id=address_id)
            request.user.default_address=address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '更新失败'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})



class UpdateTitleView(View):
    '''修改title'''

    def put(self, request, address_id):
        json_dict=json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            address = Address.objects.get(id=address_id)
            address.title=title
            address.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '更新失败'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})

class UpdatePasswordView(View):
    '''修改密码'''
    def put(self,request):
        json_data=json.loads(request.body.decode())
        old_password=json_data.get('old_password')
        new_password=json_data.get('new_password')
        new_password2=json_data.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        result = request.user.check_password(old_password)
        if not result:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '原始密码不正确'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '密码最少8位,最长20位'})

        if new_password != new_password2:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '两次输入密码不一致'})
        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400,
                                      'errmsg': '修改失败'})
        # 退出登录
        logout(request)
        response = http.JsonResponse({'code': .0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response