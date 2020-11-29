from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import GoodsCategory
from apps.goods.models import SKU, SPU, SPUSpecification
from apps.meiduo_admin.serializers.image import SKUSeriazlier
from apps.meiduo_admin.serializers.sku import SKUSerializers, SKUCategorieSerializer, GoodsSimpleSerializer, \
    GoodsSpecSerializer
from apps.meiduo_admin.utils import PageNum


class SKUView(APIView):

    def get(self,request):
        data = SKU.objects.all()
        ser = SKUSeriazlier(data, many=True)
        return Response(ser.data)


class SKUModelViewSet(ModelViewSet):
    serializer_class =SKUSerializers
    pagination_class = PageNum

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)

class SKUGoodsCategoryView(ListAPIView):

    serializer_class = SKUCategorieSerializer

    queryset = GoodsCategory.objects.filter(subs=None)


class GoodSimpleView(ListAPIView):

    serializer_class =GoodsSimpleSerializer

    queryset = SPU.objects.all()



class GoodsSpecView(ListAPIView):
    serializer_class = GoodsSpecSerializer
    def get_queryset(self):
        pk=self.kwargs.get('pk')
        return SPUSpecification.objects.filter(spu_id=pk)
