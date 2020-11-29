from django.db import transaction
from rest_framework import serializers

from apps.contents.models import GoodsCategory
from apps.goods.models import SKU, SPU, SpecificationOption, SPUSpecification, SKUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    spec_id=serializers.IntegerField()
    option_id=serializers.IntegerField()
    class Meta:
        model=SKUSpecification
        fields=('spec_id','option_id')


class SKUSerializers(serializers.ModelSerializer):
    spu_id=serializers.IntegerField()
    category_id=serializers.IntegerField()
    spu=serializers.StringRelatedField(read_only=True)
    category=serializers.StringRelatedField(read_only=True)
    specs=SKUSpecificationSerializer(many=True)


    class Meta:
        model=SKU
        fields='__all__'



    def create(self, validated_data):
        specs_data=validated_data.pop('specs')
        with transaction.atomic():
            savepoint = transaction.savepoint()
        sku=SKU.objects.create(**validated_data)
        for specs in specs_data:
            SKUSpecification.objects.create(sku=sku,**specs)
        transaction.savepoint_commit(savepoint)
        return sku


    def update(self, instance, validated_data):
        specs_data=validated_data.pop('specs')
        super().update(instance,validated_data)
        for specs in specs_data:
            SKUSpecification.objects.filter(sku=instance,spec_id=specs.get('spec_id')).update(option_id=specs.get('option_id'))

        return instance



class SKUCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoodsCategory
        fields='__all__'


class GoodsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model=SPU
        fields='__all__'

class GoodsSpecOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model=SpecificationOption
        fields=('id','value')

class GoodsSpecSerializer(serializers.ModelSerializer):
    spu=serializers.StringRelatedField()
    spu_id=serializers.IntegerField()
    options=GoodsSpecOptionSerializer(many=True)

    class Meta:
        model=SPUSpecification
        fields='__all__'

