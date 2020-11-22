from django.urls import path
from . import views

urlpatterns = [
# 商品列表页: GET /list/(?P<category_id>\d+)/skus/
    path('list/<int:category_id>/skus/', views.ListView.as_view()),
# hot / (?P < category_id > \d+) /
    path('hot/<int:category_id>/', views.HotGoodsView.as_view()),
    # 自定义商品搜索视图: GET /search/
    # 千万不要去调用as_view()，这是唯一不同的地方
    path('search/', views.MySearchView()),


]