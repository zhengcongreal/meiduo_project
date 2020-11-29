#!/usr/bin/env python

# 指定导包的路径：是为了后面的导包按照美多商城的导包方式正常导包
import sys
# sys.path.insert(导包路径列表的角标，0表示新的导包路径在最前面, '新的导包路径，这里是指向第一个meiduo_mall')
# 如何指向第一个meiduo_mall？从当前的scripts文件目录往上回退两级即可
sys.path.insert(0, '../../')

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 加载Django程序的环境
# 设置Django运行所依赖的环境变量
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 让Django进行一次初始化
import django
django.setup()


# 导入其他包
from django.template import loader
from django.conf import settings

# 导入相关模型类
from apps.goods.models import SKU
from apps.goods.goods_utils import get_categories, get_breadcrumb, get_goods_specs


# 定义静态化详情页的工具方法
def action_static_detail_html(sku):
    """
    :param sku: 要去静态化的SKU信息
    """
    # 查询要渲染页面的数据
    # 查询商品SKU信息：参数sku
    # 查询商品分类
    categories = get_categories()
    # 查询面包屑导航
    breadcrumb = get_breadcrumb(sku.category)
    # 查询商品规格信息
    goods_specs = get_goods_specs(sku)
    # 查询SKU关联的SPU，渲染商品详情，售后，包装：SPU信息可以在模板中直接使用关联查询得到 {{ sku.spu }}

    # 构造上下文字典
    context = {
        'sku': sku,
        'categories': categories,
        'breadcrumb': breadcrumb,
        'specs': goods_specs
    }

    # 使用上下文字典渲染详情页HTML文件，并得到详情页的HTML字符串
    template = loader.get_template('detail.html')
    detail_html_str = template.render(context)

    # 将详情页的HTML字符串写入到指定的静态文件中
    # file_path = '路径/front_end_pc/goods/3.html'
    file_path = os.path.join(os.path.dirname(os.path.dirname(settings.BASE_DIR)), 'front_end_pc/goods/'+str(sku.id)+'.html')
    print(settings.BASE_DIR)
    with open(file_path, 'w') as f:
        f.write(detail_html_str)


if __name__ == '__main__':
    # 脚本的入口：查询所有的sku信息，遍历他们，每遍历一个sku就生成一个对应的静态页
    skus = SKU.objects.all()
    for sku in skus:
        # print(sku.id)
        action_static_detail_html(sku)