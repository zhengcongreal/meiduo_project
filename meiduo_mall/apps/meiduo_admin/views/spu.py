from django.http import Http404
from rest_framework.generics import ListAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import GoodsCategory
from apps.goods.models import SPU, Brand
from apps.meiduo_admin.serializers.spu import SPUSerializers, BrandSerializers, SPUCategorieSerializer
from apps.meiduo_admin.utils import PageNum


class SPUModelViewSet(ModelViewSet):
    serializer_class =SPUSerializers
    pagination_class = PageNum

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SPU.objects.all()
        else:
            return SPU.objects.filter(name__contains=keyword)




class BrandListView(ListAPIView):

    serializer_class = BrandSerializers

    queryset = Brand.objects.all()


# 获取一级分类
class SPUGoodsCategoryView(ListAPIView):

    serializer_class = SPUCategorieSerializer

    queryset = GoodsCategory.objects.filter(parent=None)

# 获取二级分类
# class SPUGoodsCategory2View(APIView):
#     def get(self,request,pk):
#         try:
#             category=GoodsCategory.objects.get(pk=pk)
#         except GoodsCategory.DoesNotExist:
#             raise Http404
#         goodscategory2=category.subs.all()
#         serializer=SPUCategorieSerializer(goodscategory2,many=True)
#         return Response(serializer.data)

class SPUGoodsCategory2View(ListAPIView):
    serializer_class = SPUCategorieSerializer
    def get_queryset(self):
        pk=self.kwargs.get('pk')
        return GoodsCategory.objects.filter(parent=pk)


    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
