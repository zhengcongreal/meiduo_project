from rest_framework import serializers
from rest_framework.generics import ListAPIView

from apps.contents.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from apps.meiduo_admin.serializers.sku import SKUCategorieSerializer


class GoodsChannelSerializers(serializers.ModelSerializer):
    category=serializers.StringRelatedField(read_only=True)
    category_id=serializers.IntegerField()
    group=serializers.StringRelatedField(read_only=True)
    group_id=serializers.IntegerField()
    class Meta:
        model=GoodsChannel
        fields='__all__'

class GoodsChannelGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoodsChannelGroup
        fields=('id','name')


