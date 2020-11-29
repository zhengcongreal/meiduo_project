from django.urls import path
from apps.meiduo_admin import login
from apps.meiduo_admin.views import home, user, sku, order, spu, specs, brand, content, permission,admin

urlpatterns = [
     path('authorizations/',login.admin_jwt_token),
     # 日活统计
     path('statistical/day_active/',home.UserDailyActiveCountView.as_view()),
     # 日下单统计
     path('statistical/day_orders/',home.UserDailyOrderCountView.as_view()),
     # 月增用户统计
     path('statistical/month_increment/',home.UserMonthCountView.as_view()),
     # 用户总量统计
     path('statistical/total_count/',home.UserTotalCountView.as_view()),
     # 日增用户统计
     path('statistical/day_increment/',home.UserDailyIncrementView.as_view()),
     # 查询用户
     path('users/',user.UserListView.as_view()),
     # 获取sku表id,name
     path('skus/simple/',sku.SKUView.as_view()),
     # 获取商品3级分类
     path('skus/categories/',sku.SKUGoodsCategoryView.as_view()),

     #获取spu
     path('goods/simple/',sku.GoodSimpleView.as_view()),
     #获取spu对应的规格和选项
     path('goods/<int:pk>/specs/', sku.GoodsSpecView.as_view()),
     # 更新订单状态
     path('orders/<int:order_id>/status/',order.OrderStatusUpdateView.as_view()),

     # 获取品牌列表
     path('goods/brands/simple/',spu.BrandListView.as_view()),
     # 获取一级分类
     path('goods/channel/categories/',spu.SPUGoodsCategoryView.as_view()),
     # 获取二级三级分类
     path('goods/channel/categories/<pk>/',spu.SPUGoodsCategory2View.as_view()),
     #获取规格id
     path('goods/specs/simple/',specs.SPUSpecListView.as_view()),
     # 获取频道组
     path('goods/channel_types/',content.GoodsChannelGroupView.as_view()),
     # 获取频道管理中的一级分类
     path('goods/categories/',spu.SPUGoodsCategoryView.as_view()),
     # 1、获取权限类型列表数据
     path('permission/content_types/', permission.ContentTypeAPIView.as_view()),
     # 获取权限表数据
     path('permission/simple/', permission.GroupSimpleAPIView.as_view()),
     # 获取分组表数据
     path('permission/groups/simple/', admin.AdminSimpleAPIView.as_view()),

]





from .views import image
from rest_framework.routers import DefaultRouter

#创建router实例
router = DefaultRouter()
#注册路由
router.register(r'skus/images',image.ImageView,basename='image')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls


from .views import sku


router = DefaultRouter()

router.register(r'skus',sku.SKUModelViewSet,basename='skus')

urlpatterns+=router.urls

router.register(r'orders',order.OrderModelViewSet,basename='orders')
urlpatterns+=router.urls

router.register(r'goods/brands',brand.BrandModelViewSet,basename='brands')
urlpatterns+=router.urls

router.register(r'goods/channels',content.GoodsGroupModelViewSet,basename='channels')
urlpatterns+=router.urls


router.register(r'goods/specs',specs.SPUSpecsModelViewSet,basename='specs')
urlpatterns+=router.urls

router.register(r'goods',spu.SPUModelViewSet,basename='goods')
urlpatterns+=router.urls


router.register(r'specs/options',specs.SPUSpecsOptionsModelViewSet,basename='goods')
urlpatterns+=router.urls


router.register(r'permission/perms',permission.PermissionView,basename='perms')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls


router.register(r'permission/groups',permission.GroupView,basename='groups')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls


router.register(r'permission/admins',admin.AdminView,basename='admins')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls


