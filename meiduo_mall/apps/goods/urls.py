from django.urls import path
from . import views

urlpatterns = [
# 商品列表页: GET /list/(?P<category_id>\d+)/skus/
    path('list/<int:category_id>/skus/', views.ListView.as_view()),
# hot / (?P < category_id > \d+) /
    path('hot/<int:category_id>/', views.HotGoodsView.as_view()),



]