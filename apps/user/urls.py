from django.conf.urls import url
from apps.user import views

urlpatterns = [
    url(r'^register$',views.RegisterView.as_view(),name='register'), #注册
    url(r'^login$',views.LoginView.as_view(),name='login'), #登陆
    url(r'^active/(.*)',views.ActiveView.as_view(),name='active'),#激活
    url(r'^send_agin$',views.SendAginView.as_view(),name='send_agin'), # 再次激活
    url(r'^logout$',views.LogoutView.as_view(),name='logout'), # 登出

    #-----用户信息页面-------
    url(r'^$',views.UserInfoView.as_view(),name='user'),  # 用户信息页面
    url(r'^order/(\d+)$',views.UserOrderView.as_view(),name='order'), # 用户订单页面
    url(r'^address$',views.UserAddressView.as_view(),name='address'),# 用户收货地址页面
]
