from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import JsonResponse
import logging

logger = logging.getLogger('django')
from apps.areas.models import Area


class ProvinceAreasView(View):
    def get(self, request):
        # 增加: 判断是否有缓存
        province_list = cache.get('province_list')

        if not province_list:
            try:
                # 查询省级数据
                Province_Model_List = Area.objects.filter(parent__isnull=True)
                # 整理省级数据
                province_list = []
                for province in Province_Model_List:
                    province_list.append({'id': province.id, 'name': province.name})
                cache.set('province_list', province_list, 3600)
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': 400, 'errmsg': '查询省份数据出错！'})
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})


class SubAreasView(View):
    def get(self, request, pk):
        """提供市或区地区数据
              1.查询市或区数据
              2.序列化市或区数据
              3.响应市或区数据
              4.补充缓存数据
              """
        # 判断是否有缓存
        sub_data = cache.get('sub_area_' + str(pk))
        if not sub_data:
            try:
                # 1.查询市或区数据
                # 查询当前的父级地区：省份或者城市
                # sub_model_list=Area.objects.filter(parent=pk)
                parent_areas = Area.objects.get(id=pk)
                #  查询省份数据
                # 查询当前父级地区的子级（一查多）：省份查城市、城市查区县，要查询父级对应的所有子级，所以会调用all()
                sub_model_list = parent_areas.subs.all()
                # parent_model=Area.objects.get(pk=pk)
                # 2.整理市或区数据
                sub_list = []
                for sub_model in sub_model_list:
                    sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                sub_data = {
                    'id':parent_areas.id,
                    'name':parent_areas.name,
                    'subs': sub_list
                }
                cache.set('sub_area_' + str(pk), sub_data, 3600)
            except Exception as e:
                logger.error(e)
                JsonResponse({'code': 0, 'errmsg': '获取数据出错！'})

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': sub_data})
