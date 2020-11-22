import base64
import json
import pickle

from django import http
from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU

class CartsSimpleView(View):
    def get(self,request):
        # 展示购物车
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 展示redis购物车
            cart_items = redis_conn.hgetall('carts_%s' % request.user.id)
            car_select = redis_conn.smembers('selected_%s' % request.user.id)
            # 将 redis 中的数据构造成跟 cookie 中的格式一致
            # 方便统一查询
            cart_dict = {}
            for sku_id, count in cart_items.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in car_select
                }

        else:
            # 展示cookie购物车

            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                # 用户从来没有操作过购物车
                cart_dict = {}

        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url,
            })

        return http.JsonResponse({'code': 0,
                                  'errmsg': 'ok',
                                  'cart_skus': cart_skus})


class SelectAllView(View):
    '''全选购物车'''
    def put(self,request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            skus_items = redis_conn.hgetall('carts_%s' % request.user.id)
            sku_ids = skus_items.keys()
            if selected:
                redis_conn.sadd('selected_%s'%request.user.id,*sku_ids)
            else:
                redis_conn.srem('selected_%s'%request.user.id,*sku_ids)
            return http.JsonResponse({'code': 0, 'errmsg': '全选成功！'})

        else:
            # 用户未登录，操作cookie购物车
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict={}
            for sku in cart_dict.keys():
                cart_dict[sku][selected]=selected
            cart_data=base64.b64encode(pickle.dumps(cart_dict)).decode()
            response=http.JsonResponse({'code':0,'errmsg':'全选成功！'})
            response.set_cookie('carts',cart_data)

            return  response






class CartsView(View):
    """购物车管理"""

    def delete(self,request):
        '''删除购物车'''
        json_dict=json.loads(request.body.decode())
        sku_id=json_dict.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('找不到该商品')
        # redis删除
            # 判断用户是否登录
        if request.user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % request.user.id, sku_id)
            pl.srem('selected_%s' % request.user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': 0, 'errmsg': 'ok'})
        # cookie删除
        else:
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 用户从来没有操作过购物车
                cart_dict = {}

            if sku_id in cart_dict:
                del cart_dict[sku_id]

            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = http.JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', cart_data)
            return response

    def put(self,request):
        '''修改购物车'''
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        if not all([sku_id, count]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('找不到该商品')
        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('count参数有误！')
        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        if request.user.is_authenticated:

            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset('carts_%s' % request.user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % request.user.id, sku_id)
            else:
                pl.srem('selected_%s'%request.user.id,sku_id)
            pl.execute()


            return http.JsonResponse({'code':0,'errmsg':'ok',
                                      'cart_sku':
                                          {'id':sku_id,
                                           'count':count,
                                           'selected':selected}
                                      })
        else:
            # 用户未登录，操作cookie购物车
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 用户从来没有操作过购物车
                cart_dict = {}
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            cart_sku={'id':sku_id,
                      'count':count,
                      'selected':selected}

            response = http.JsonResponse({'code': 0, 'errmsg': 'ok','cart_sku':cart_sku})
            response.set_cookie('carts', cart_data)
            return response

    def get(self,request):

        # 展示购物车

        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 展示redis购物车
            cart_items=redis_conn.hgetall('carts_%s'%request.user.id)
            car_select=redis_conn.smembers('selected_%s'%request.user.id)
            # 将 redis 中的数据构造成跟 cookie 中的格式一致
            # 方便统一查询
            cart_dict={}
            for sku_id,count in cart_items.items():
                cart_dict[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in car_select
                }

        else:
            # 展示cookie购物车

            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                # 用户从来没有操作过购物车
                cart_dict = {}

        sku_ids=cart_dict.keys()
        skus=SKU.objects.filter(id__in=sku_ids)
        cart_skus=[]
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': cart_dict.get(sku.id).get('selected'),
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                # 'amount':sku.price*cart_dict.get(sku.id).get('count'),
            })

        return http.JsonResponse({'code': 0,
                                  'errmsg': 'ok',
                                  'cart_skus': cart_skus})

    def post(self,request):
        """添加购物车"""
        # 接收参数
        json_dict=json.loads(request.body.decode())
        sku_id=json_dict.get('sku_id')
        count=json_dict.get('count')
        selected=json_dict.get('selected',True)
        # 校验参数
        if not all([sku_id,count]):
            return http.JsonResponse({'code':400,'errmsg':'缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('找不到该商品')
        try:
            count=int(count)
        except Exception:
            return HttpResponseForbidden('count参数有误！')
        if selected:
            if not isinstance(selected,bool):
                return HttpResponseForbidden('参数selected有误')


         # 判断用户是否登录
        if request.user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn=get_redis_connection('carts')
            pl=redis_conn.pipeline()
            pl.hincrby('carts_%s'%request.user.id,sku_id,count)
            if selected:
                pl.sadd('selected_%s'%request.user.id,sku_id)
            pl.execute()
            return http.JsonResponse({'code':0,'errmsg':'添加购物车成功！'})
        else:
            # 用户未登录，操作cookie购物车
            cookie_cart=request.COOKIES.get('carts')
            if cookie_cart:
                cart_dict=pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 用户从来没有操作过购物车
                cart_dict={}

            # 判断要加入购物车的商品是否已经在购物车中
            # 如有相同商品，累加求和，反之，直接赋值
            # 我们判断用户之前是否将该商品加入过购物车, 如果加入过
            # 则只需要让数量增加即可.
            # 如果没有存在过, 则需要创建, 然后增加:
            # 形式如下所示:
            # {
            #     '<sku_id>': {
            #         'count': '<count>',
            #         'selected': '<selected>',
            #     },
            #     ...
            # }
            if sku_id in cart_dict:
                count+=cart_dict[sku_id]['count']
            cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }
            cart_data=base64.b64encode(pickle.dumps(cart_dict)).decode()
            response= http.JsonResponse({'code': 0, 'errmsg': '添加购物车成功！'})
            response.set_cookie('carts',cart_data)
            return response