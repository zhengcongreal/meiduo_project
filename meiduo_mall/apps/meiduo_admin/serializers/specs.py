from rest_framework import serializers

from apps.goods.models import SPUSpecification, SpecificationOption


class SPUSpecificationSerializer(serializers.ModelSerializer):
    spu_id=serializers.IntegerField()
    spu=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=SPUSpecification
        fields='__all__'


class SPUSpecificationOptionsSerializer(serializers.ModelSerializer):
    spec_id=serializers.IntegerField()
    spec=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=SpecificationOption
        fields='__all__'

class SPUSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model=SPUSpecification
        fields=('id','name')
