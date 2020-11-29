from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.contents.models import GoodsChannel, GoodsChannelGroup
from apps.meiduo_admin.serializers.content import GoodsChannelSerializers, GoodsChannelGroupSerializer
from apps.meiduo_admin.utils import PageNum


class GoodsGroupModelViewSet(ModelViewSet):
    serializer_class =GoodsChannelSerializers
    pagination_class = PageNum
    queryset = GoodsChannel.objects.all()

class GoodsChannelGroupView(ListAPIView):
    serializer_class = GoodsChannelGroupSerializer
    queryset = GoodsChannelGroup.objects.all()
