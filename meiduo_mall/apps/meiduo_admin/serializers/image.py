from rest_framework import serializers
from apps.goods.models import SKUImage
from rest_framework import serializers
from apps.goods.models import SKU

class ImageSeriazlier(serializers.ModelSerializer):
    # 返回图片关联的sku的id值
    sku=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=SKUImage
        fields=('sku','image','id')

class SKUSeriazlier(serializers.ModelSerializer):
    class Meta:
        model=SKU
        fields=('id','name')
