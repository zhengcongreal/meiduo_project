from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage
from apps.meiduo_admin.utils import PageNum
from apps.meiduo_admin.serializers.image import ImageSeriazlier
from fdfs_client.client import Fdfs_client
class ImageView(ModelViewSet):
    # 图片序列化器
    serializer_class = ImageSeriazlier
    # 图片查询集
    queryset = SKUImage.objects.all()
    # 分页
    pagination_class = PageNum

    # 重写拓展类的保存业务逻辑
    def create(self, request, *args, **kwargs):
        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 获取前端传递的image文件
        data = request.data.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')
        # 保存图片
        img = SKUImage.objects.create(sku_id=sku_id, image=image_url)
        # 返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku_id,
                'image': img.image.url
            },
            status=201  # 前端需要接受201状态
        )

    # 重写拓展类的更新业务逻辑
    def update(self, request, *args, **kwargs):

        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 查询图片对象
        sku_image = SKUImage.objects.get(id=kwargs['pk'])
        # 在storage中删除图片
        del_res = client.delete_file(str(sku_image.image))
        if del_res[0] != 'Delete file successed.':
            return Response(status=403)
        # 获取前端传递的image文件
        data = request.data.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')

        # 更新图片
        sku_image.image = image_url
        sku_image.save()
        # 返回结果
        return Response(
            {
                'id': sku_image.id,
                'sku': sku_id,
                'image': sku_image.image.url
            },
            status=201  # 前端需要接受201状态码
        )

    # 重写拓展类的删除业务逻辑
    def destroy(self,request,*args, **kwargs):

        # 创建FastDFS连接对象

        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 查询图片对象
        sku_image = SKUImage.objects.get(id=kwargs['pk'])
        storage_img=sku_image.image
        # 在storage中删除图片
        res=client.delete_file(str(storage_img))
        if res[0] != 'Delete file successed.':
            return Response(status=403)
        # 删除数据库中的图片
        sku_image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


