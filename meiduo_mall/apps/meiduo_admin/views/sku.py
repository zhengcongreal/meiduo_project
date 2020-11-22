from rest_framework.views import APIView
from rest_framework.response import Response
from apps.goods.models import SKU
from apps.meiduo_admin.serializers.sku import SKUSeriazlier


class SKUView(APIView):

    def get(self,request):
        data = SKU.objects.all()
        ser = SKUSeriazlier(data, many=True)
        return Response(ser.data)
