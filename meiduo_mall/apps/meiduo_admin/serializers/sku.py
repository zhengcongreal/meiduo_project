from rest_framework import serializers
from apps.goods.models import SKU

class SKUSeriazlier(serializers.ModelSerializer):
    class Meta:
        model=SKU
        fields=('id','name')
