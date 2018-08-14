from django.conf.urls import url
from apps.goods import views

urlpatterns = [
    url(r'^index$',views.IndexView.as_view(),name='index'), #首页
    url(r'^detail/(\d+)',views.GoodsDetailView.as_view(),name='detail'), # 商品详情页
    url(r'^list/(?P<id>\d+)/(?P<page>\d+)',views.GoodsListView.as_view(),name='list'), #显示同种类的商品列表
]
