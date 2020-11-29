from fdfs_client.client import Fdfs_client

from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import Brand
from apps.meiduo_admin.serializers.brand import BrandSerializer
from apps.meiduo_admin.utils import PageNum


class BrandModelViewSet(ModelViewSet):
    serializer_class =BrandSerializer
    queryset = Brand.objects.all()
    pagination_class = PageNum

    # 重写拓展类的保存业务逻辑
    def create(self, request, *args, **kwargs):
        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 获取前端传递的image文件
        data = request.data.get('logo')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']

        # 保存图片
        brand = Brand.objects.create(name=request.data.get('name'),first_letter=request.data.get('first_letter'),logo=image_url)
        # 返回结果
        return Response(
            {
                'id': brand.id,
                'name': brand.name,
                'logo': brand.logo.url,
                'first_letter': brand.first_letter
            }
            ,status=201
        )

        # 重写拓展类的更新业务逻辑

    def update(self, request, *args, **kwargs):

        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 查询图片对象
        brand = Brand.objects.get(id=kwargs['pk'])
        # 在storage中删除图片
        del_res = client.delete_file(str(brand.logo))
        if del_res[0] != 'Delete file successed.':
            return Response(status=403)

        # 上传图片到fastDFS
        data = request.data.get('logo')

        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']

        # 更新品牌信息
        brand.logo=image_url
        brand.name=request.data.get('name')
        brand.first_letter=request.data.get('first_letter')
        brand.save()

        return Response(
            {
                'id': brand.id,
                'name': brand.name,
                'logo': brand.logo.url,
                'first_letter': brand.first_letter
            }

        )


    def destroy(self,request,*args, **kwargs):

        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 查询图片对象
        brand = Brand.objects.get(id=kwargs['pk'])
        # 在storage中删除图片
        del_res = client.delete_file(str(brand.logo))
        if del_res[0] != 'Delete file successed.':
            return Response(status=403)
        # 删除数据库中的图片
        brand.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
