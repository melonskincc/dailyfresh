from django.db import models
from db.base_model import BaseModel

# Create your models here.

class OrderInfo(BaseModel):
    """订单信息模型类"""
    #订单信息
    status_choices=(
        (1,'待付款'),
        (2,'待发货'),
        (3,'待收货'),
        (4,'待评价'),
        (5,'已完成')
    )
    #支付方式
    pay_method_choices=(
        (1,'货到付款'),
        (2,'微信支付'),
        (3,'支付宝支付'),
        (4,'银联支付')
    )

    ORDER_STATUS={
        1:'待支付',
        2:'待发货',
        3:'待收货',
        4:'待评价',
        5:'已完成'
    }

    PAY_METHODS = {
        '1': "货到付款",
        '2': "微信支付",
        '3': "支付宝",
        '4': '银联支付'
    }
    order_id=models.CharField(primary_key=True,max_length=128,verbose_name='订单编号')
    user=models.ForeignKey('user.User',verbose_name='用户')
    status=models.SmallIntegerField(choices=status_choices,default=1,verbose_name='订单状态')
    address=models.ForeignKey('user.Address',verbose_name='地址')
    transit_price=models.DecimalField(max_digits=6,decimal_places=2,verbose_name='订单运费')
    total_count=models.CharField(max_length=20,verbose_name='商品总数')
    total_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')
    pay_method=models.SmallIntegerField(choices=pay_method_choices,default=3,verbose_name='支付方式')
    trande_no=models.CharField(max_length=128,default='',verbose_name='支付编号')

    class Meta:
        db_table='df_order_info'
        verbose_name='订单信息'
        verbose_name_plural=verbose_name

class OrderGoods(BaseModel):
    """订单商品模型类"""
    order=models.ForeignKey('OrderInfo',verbose_name='订单信息')
    goods_sku=models.ForeignKey('goods.GoodsSKU',verbose_name='商品SKU')
    count=models.IntegerField(default=1,verbose_name='商品数目')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    comment=models.CharField(max_length=256,default='',verbose_name='评论')

    class Meta:
        db_table='df_order_goods'
        verbose_name='订单商品'
        verbose_name_plural=verbose_name