from django.contrib.auth.models import Permission
from rest_framework import serializers

from rest_framework import serializers
from django.contrib.auth.models import ContentType
from django.contrib.auth.models import Group

class PermissionSerialzier(serializers.ModelSerializer):
    """
    用户权限表序列化器
    """
    class Meta:
        model=Permission
        fields="__all__"

class ContentTypeSerialzier(serializers.ModelSerializer):
    """
    权限类型序列化器
    """
    class Meta:
        model=ContentType
        fields=('id','name')


class GroupSerialzier(serializers.ModelSerializer):

    class Meta:
        model=Group
        fields="__all__"
