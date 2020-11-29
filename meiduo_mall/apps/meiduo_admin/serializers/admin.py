from rest_framework import serializers

from apps.users.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"
        extra_kwargs={
            'password':{
                'write_only': True
            }
        }
    # 重写父类方法，增加管理员权限属性
    def create(self, validated_data):
        # 调用父类方法创建管理员用户
        admin = super().create(validated_data)
        # 用户密码加密
        password = validated_data['password']
        admin.set_password(password)
        # 设置管理员
        admin.is_staff = True
        # 保存数据
        admin.save()

        return admin

    def update(self, instance, validated_data):
        # 调用父类实现数据更新
        super().update(instance, validated_data)
        # 获取密码,并进行判断是否用户修改了密码
        password = validated_data.get('password')
        if password is not None:
            instance.set_password(password)
            instance.save()

        return instance
