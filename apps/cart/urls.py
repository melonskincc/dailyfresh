from django.conf.urls import url
from apps.cart import views

urlpatterns = [
    url(r'^show$',views.CartShowView.as_view(),name='show'),# 显示购物车页面
    url(r'^add$',views.CartAddView.as_view(),name='add'),  #购物车增加数据
    url(r'^delete$',views.CartDeleteView.as_view(),name='delete'), #刪除購物車記錄
    url(r'^update$',views.CartUpdateView.as_view(),name='update'),# 更新購物車數據
]
