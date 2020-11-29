from rest_framework import serializers
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods

class SKUSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        print("___instance___")
        print(instance.default_image)
        # instance['default_image_url'] = instance.default_image
        ret={
            'name':instance.name,
            'default_image_url':instance.default_image.url
        }
        return ret
    # def to_internal_value(self, data):
    #     print("---to_internal_value---")
    #     print(type(data))
    #     print(data)
    #     return data

    class Meta:
        model=SKU
        fields='__all__'

class OrderGoodsSerializer(serializers.ModelSerializer):
    # order=serializers.StringRelatedField()
    sku=SKUSerializer(read_only=True)
    class Meta:
        model=OrderGoods
        fields='__all__'

class OrderSerializer(serializers.ModelSerializer):
    user=serializers.StringRelatedField()
    skus=OrderGoodsSerializer(many=True,read_only=True)
    class Meta:
        model=OrderInfo
        fields='__all__'

