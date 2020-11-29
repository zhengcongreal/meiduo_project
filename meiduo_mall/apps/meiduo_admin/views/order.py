from django.http import Http404
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.order import OrderSerializer
from apps.meiduo_admin.utils import PageNum
from apps.orders.models import OrderInfo


class OrderModelViewSet(ModelViewSet):
    serializer_class =OrderSerializer
    pagination_class = PageNum

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)


class OrderStatusUpdateView(APIView):
    def put(self,request,order_id):
        try:
            order=OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            raise Http404
        order.status=request.data.get('status')
        order.save()
        return Response({'order_id':order.order_id,'status':order.status})
