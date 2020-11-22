################# 获取商品分类的工具方法 #################
from apps.contents.models import GoodsChannel


def get_categories():
    # 准备商品分类数据的字典容器
    categories = {}
    # 查询所有的37个频道(一级分类)
    # GoodsChannel.objects.all().order_by('group_id', 'sequence')
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历所有的频道，取出每一个频道
    for channel in channels:
        # 通过频道数据关联的组取出对应的组号
        group_id = channel.group.id
        # 将group_id作为categories字段的key
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 获取当前频道关联的一级分类（一个频道对应一个一级分类）
        cat1 = channel.category
        # 添加每组中对应的频道数据
        categories[group_id]['channels'].append({
            "id": channel.id,
            "name": cat1.name,
            "url": channel.url
        })

        # 添加每组中的二级和三级分类
        for cat2 in cat1.subs.all():
            # 使用二级分类查询关联的三级分类
            sub_cats = []
            for cat3 in cat2.subs.all():
                sub_cats.append({
                    "id": cat3.id, # 三级分类ID
                    "name": cat3.name # 三级分类名字
                })

            categories[group_id]['sub_cats'].append({
                "id": cat2.id, # 二级分类ID
                "name": cat2.name, # 二级分类名字
                "sub_cats": sub_cats # 二级关联的三级分类
            })

    return categories


################# 获取面包屑导航的工具方法 #################
def get_breadcrumb(cat3):
    """
    获取面包屑导航
    :param cat3: 三级分类
    :return: 面包屑导航字典
    """
    # 获取二级和一级分类
    cat2 = cat3.parent
    cat1 = cat2.parent

    # 构造面包屑导航字典
    breadcrumb = {
        'cat1': cat1.name,
        'cat2': cat2.name,
        'cat3': cat3.name
    }

    return breadcrumb


################# 获取商品规格的工具方法 #################
def get_goods_specs(sku):
    # 构建当前商品的规格键
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数（选项）的sku字典
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 以下代码为：在每个选项上绑定对应的sku_id值
    # 获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(goods_specs):
        return
    for index, spec in enumerate(goods_specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        spec_options = spec.options.all()
        for option in spec_options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.spec_options = spec_options

    return goods_specs