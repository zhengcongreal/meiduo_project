from rest_framework import serializers
from apps.goods.models import SKUImage

class ImageSeriazlier(serializers.ModelSerializer):
    # 返回图片关联的sku的id值
    sku=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=SKUImage
        fields=('sku','image','id')
