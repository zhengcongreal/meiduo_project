from django.db import models

# Create your models here.
from meiduo_mall.utils.models import BaseModel


class ContentCategory(BaseModel):
    """广告类别表"""

    # 广告类别名称
    name=models.CharField(max_length=50,verbose_name='名称')
    # 广告的类别键名:
    key=models.CharField(max_length=50,verbose_name='类别键名')
    class Meta:
        db_table='tb_content_category'
        verbose_name='广告内容类别'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name
    objects=models.Manager()

class Content(BaseModel):
    """广告内容表"""

    # 外键, 关联广告类别
    category=models.ForeignKey(ContentCategory,on_delete=models.PROTECT,verbose_name='类别')
    title=models.CharField(max_length=50,verbose_name='标题')
    # 广告被点击后跳转的 url
    url = models.CharField(max_length=300,
                           verbose_name='内容链接')
    # 广告图片地址保存字段:
    image=models.ImageField(null=True,blank=True,verbose_name='图片')
    # 文字性广告保存在该字段:
    text = models.TextField(null=True,
                            blank=True,
                            verbose_name='内容')
    # 广告内容排序:
    sequence=models.IntegerField(verbose_name='排序')
    # 广告是否展示的状态:
    status=models.BooleanField(default=True,verbose_name='是否展示')

    class Meta:
        db_table = 'tb_content'

    def __str__(self):
        return self.category.name + ': ' + self.title

class GoodsCategory(BaseModel):
    """
      商品分类表对应的内容, 自关联
      """
    # 分类的名称
    name=models.CharField(max_length=10,verbose_name='名称')
    # 分类的上级id (分类一共有三级)
    parent=models.ForeignKey('self', related_name='subs',null=True,blank=True,verbose_name='父类别',on_delete=models.CASCADE)

    # 设置分类表的属性
    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    # 返回分类名称
    def __str__(self):
        return self.name

    objects=models.Manager()
class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    name = models.CharField(max_length=20, verbose_name='频道组名')

    class Meta:
        db_table = 'tb_channel_group'

    def __str__(self):
        return self.name

class GoodsChannel(BaseModel):
    """
    商品频道表展示的内容
    """
    # 当前商品频道属于哪个组
    group=models.ForeignKey(GoodsChannelGroup,on_delete=models.CASCADE,verbose_name='频道组名')
    # 频道对应的一级分类id
    category=models.ForeignKey(GoodsCategory,on_delete=models.CASCADE,verbose_name='顶级商品类别')
    # 当前频道点击后跳转的链接地址
    url = models.CharField(max_length=50,
                           verbose_name='频道页面链接')
    # 这组频道的先后顺序
    sequence=models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name
    objects=models.Manager()



