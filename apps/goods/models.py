from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
# Create your models here.

class GoodsKind(BaseModel):
    """商品种类（大种类）模型类"""
    name=models.CharField(max_length=20,verbose_name='种类名称')
    logo=models.CharField(max_length=20,verbose_name='标识')
    image=models.ImageField(upload_to='kind',verbose_name='商品种类图片')

    class Meta:
        db_table='df_goods_kind'
        verbose_name='商品种类'
        verbose_name_plural=verbose_name

class GoodsSPU(BaseModel):
    """商品SPU（小种类）模型类"""
    name=models.CharField(max_length=20,verbose_name='商品SPU名称')
    # 富文本类型：带有格式的文本
    detail=HTMLField(blank=True,verbose_name='商品详情')

    class Meta:
        db_table='df_goods_spu'
        verbose_name='商品SPU'
        verbose_name_plural=verbose_name

class GoodsSKU(BaseModel):
    """商品SKU（具体）模型类"""

    #商品状态选择
    status_choices=(
        (0,'下架'),
        (1,'上架'),
    )

    name=models.CharField(max_length=20,verbose_name='商品名称')
    stock=models.IntegerField(default=0,verbose_name='商品库存')
    goods_kind=models.ForeignKey('GoodsKind',verbose_name='商品种类')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='单价')
    sales=models.IntegerField(default=0,verbose_name='销量')
    desc=models.CharField(max_length=256,verbose_name='商品简介')
    status=models.SmallIntegerField(choices=status_choices,default=1,verbose_name='商品状态')
    unit=models.CharField(max_length=20,verbose_name='单位')
    image=models.ImageField(upload_to='goods',verbose_name='默认图片')
    goods_spu=models.ForeignKey('GoodsSPU',verbose_name='商品SPU')

    class Meta:
        db_table='df_goods_sku'
        verbose_name='商品'
        verbose_name_plural=verbose_name

class GoodsImage(BaseModel):
    """商品图片模型类"""
    image=models.ImageField(upload_to='goods',verbose_name='商品图片')
    goods_sku=models.ForeignKey('GoodsSKU',verbose_name='商品')

    class Meta:
        db_table='df_goods_image'
        verbose_name='商品图片'
        verbose_name_plural=verbose_name

class IndexGoodsBanner(BaseModel):
    """首页商品轮播模型类"""
    goods_sku=models.ForeignKey('GoodsSKU',verbose_name='商品SKU')
    image=models.ImageField(upload_to='banner',verbose_name='轮播图片')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序') # 0,1,2,3

    class Meta:
        db_table='df_index_banner_goods'
        verbose_name='首页轮播商品'
        verbose_name_plural=verbose_name

class IndexKindGoodsShow(BaseModel):
    """首页商品种类展示模型"""
    display_choices=(
        (0,'标题'),
        (1,'图片')
    )
    goods_kind=models.ForeignKey('GoodsKind',verbose_name='商品种类')
    goods_sku=models.ForeignKey('GoodsSKU',verbose_name='商品SKU')
    display_type=models.SmallIntegerField(choices=display_choices,verbose_name='展示类型')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table='df_index_kind_goods'
        verbose_name='首页分类展示商品'
        verbose_name_plural=verbose_name

class IndexPromotionBanner(BaseModel):
    """首页促销活动模型类"""
    image=models.ImageField(upload_to='banner',verbose_name='活动图片')
    url=models.CharField(max_length=200,verbose_name='活动链接')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序')
    name=models.CharField(max_length=30,verbose_name='活动名称')

    class Meta:
        db_table='df_index_promotion'
        verbose_name='促销活动'
        verbose_name_plural=verbose_name