# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('count', models.IntegerField(default=1, verbose_name='商品数目')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')),
                ('comment', models.CharField(default='', max_length=256, verbose_name='评论')),
            ],
            options={
                'db_table': 'df_order_goods',
                'verbose_name': '订单商品',
                'verbose_name_plural': '订单商品',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('order_id', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='订单编号')),
                ('status', models.SmallIntegerField(default=1, choices=[(1, '待付款'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态')),
                ('transit_price', models.DecimalField(max_digits=6, decimal_places=2, verbose_name='订单运费')),
                ('total_count', models.CharField(max_length=20, verbose_name='商品总数')),
                ('total_price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')),
                ('pay_method', models.SmallIntegerField(default=3, choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝支付'), (4, '银联支付')], verbose_name='支付方式')),
                ('trande_no', models.CharField(default='', max_length=128, verbose_name='支付编号')),
            ],
            options={
                'db_table': 'df_order_info',
                'verbose_name': '订单信息',
                'verbose_name_plural': '订单信息',
            },
        ),
    ]
