from django import http
from django.core.paginator import Paginator,EmptyPage
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import GoodsCategory
from apps.goods.models import SKU
from apps.goods.utils import get_breadcrumb





class HotGoodsView(View):

    def get(self,request,category_id):
        '''热销排行'''

        try:
            sku_set = SKU.objects.filter(is_launched=True, category_id=category_id).order_by('-sales')[:2]
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400,
                                 'errmsg': '获取mysql数据出错'})


        sku_hot_list=[]
        for sku in sku_set:
            sku_hot_list.append({
                        "id":sku.id,
                        "default_image_url":sku.default_image.url,
                        "name":sku.name,
                        "price":sku.price
            })

        return http.JsonResponse({
                                "code": "0",
                                "errmsg": "OK",
                                "hot_skus":sku_hot_list
                                })





class ListView(View):
    def get(self,request,category_id):
        '''商品列表'''
        page=request.GET.get('page')
        page_size=request.GET.get('page_size')
        ordering=request.GET.get('ordering')
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:

            return http.JsonResponse({'code':0,'errmsg':'获取category_id失败！'})
        try:
            sku_set=SKU.objects.filter(is_launched=True,category=category).order_by(ordering)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400,
                                 'errmsg': '获取mysql数据出错'})
        # 面包屑导航
        breadcrumb=get_breadcrumb(category)

        paginator=Paginator(sku_set,page_size)
        try:
            # 获取分页数据
            paginator_set=paginator.page(page)
        except EmptyPage:
            return http.JsonResponse({'code': 0, 'errmsg': '获取分页数据失败！'})
        total_page=paginator.num_pages

        sku_list=[]
        for sku in paginator_set:
            sku_list.append({
                'id': sku.id,
                'default_image_url':sku.default_image.url,
                'name': sku.name,
                'price': sku.price

            })


        return http.JsonResponse({
                "code": 0,
                "errmsg": "ok",
                "breadcrumb": breadcrumb,  # 面包屑数据
                "list":sku_list,
                "count": total_page  # 分页总数

        })
