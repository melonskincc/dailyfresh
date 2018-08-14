from django.conf.urls import url
from apps.order import views

urlpatterns = [
    url(r'^place$',views.PlaceOrderView.as_view(),name='place'), #提交订单地址页面
    url(r'^create$',views.CreateOrderView.as_view(),name='create'),#创建订单
    url(r'^pay$',views.PayOrderView.as_view(),name='pay'),#返回支付宝付款页面
    url(r'^check$',views.OrderCheckView.as_view(),name='check'), #支付宝回调的页面
    url(r'^comment/(\d+)$',views.OrderCommentView.as_view(),name='comment'),#评价页面
]
