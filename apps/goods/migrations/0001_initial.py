# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='goods', verbose_name='商品图片')),
            ],
            options={
                'db_table': 'df_goods_image',
                'verbose_name': '商品图片',
                'verbose_name_plural': '商品图片',
            },
        ),
        migrations.CreateModel(
            name='GoodsKind',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(max_length=20, verbose_name='种类名称')),
                ('logo', models.CharField(max_length=20, verbose_name='标识')),
                ('image', models.ImageField(upload_to='kind', verbose_name='商品种类图片')),
            ],
            options={
                'db_table': 'df_goods_kind',
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
            },
        ),
        migrations.CreateModel(
            name='GoodsSKU',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(max_length=20, verbose_name='商品名称')),
                ('stock', models.IntegerField(default=0, verbose_name='商品库存')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('desc', models.CharField(max_length=256, verbose_name='商品简介')),
                ('status', models.SmallIntegerField(default=1, choices=[(0, '下架'), (1, '上架')], verbose_name='商品状态')),
                ('unit', models.CharField(max_length=20, verbose_name='单位')),
                ('image', models.ImageField(upload_to='goods', verbose_name='默认图片')),
                ('goods_kind', models.ForeignKey(to='goods.GoodsKind', verbose_name='商品种类')),
            ],
            options={
                'db_table': 'df_goods_sku',
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
            },
        ),
        migrations.CreateModel(
            name='GoodsSPU',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(max_length=20, verbose_name='商品SPU名称')),
                ('detail', tinymce.models.HTMLField(blank=True, verbose_name='商品详情')),
            ],
            options={
                'db_table': 'df_goods_spu',
                'verbose_name': '商品SPU',
                'verbose_name_plural': '商品SPU',
            },
        ),
        migrations.CreateModel(
            name='IndexGoodsBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='banner', verbose_name='轮播图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('goods_sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU')),
            ],
            options={
                'db_table': 'df_index_banner_goods',
                'verbose_name': '首页轮播商品',
                'verbose_name_plural': '首页轮播商品',
            },
        ),
        migrations.CreateModel(
            name='IndexKindGoodsShow',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('display_type', models.SmallIntegerField(choices=[(0, '标题'), (1, '图片')], verbose_name='展示类型')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('goods_kind', models.ForeignKey(to='goods.GoodsKind', verbose_name='商品种类')),
                ('goods_sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU')),
                ('goods_spu', models.ForeignKey(to='goods.GoodsSPU', verbose_name='商品SPU')),
            ],
            options={
                'db_table': 'df_index_kind_goods',
                'verbose_name': '首页分类展示商品',
                'verbose_name_plural': '首页分类展示商品',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotionBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='banner', verbose_name='活动图片')),
                ('url', models.CharField(max_length=200, verbose_name='活动链接')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('name', models.CharField(max_length=30, verbose_name='活动名称')),
            ],
            options={
                'db_table': 'df_index_promotion',
                'verbose_name': '促销活动',
                'verbose_name_plural': '促销活动',
            },
        ),
        migrations.AddField(
            model_name='goodssku',
            name='goods_spu',
            field=models.ForeignKey(to='goods.GoodsSPU', verbose_name='商品SPU'),
        ),
        migrations.AddField(
            model_name='goodsimage',
            name='goods_sku',
            field=models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品'),
        ),
    ]
