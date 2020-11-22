from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage
from apps.meiduo_admin.utils import PageNum
from apps.meiduo_admin.serializers.image import ImageSeriazlier

class ImageView(ModelViewSet):
    # 图片序列化器
    serializer_class = ImageSeriazlier
    # 图片查询集
    queryset = SKUImage.objects.all()
    # 分页
    pagination_class = PageNum

    # 重写拓展类的保存业务逻辑
    def create(self, request, *args, **kwargs):
        from fdfs_client.client import Fdfs_client
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
