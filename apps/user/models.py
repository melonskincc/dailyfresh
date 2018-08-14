from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser,BaseModel):  # 继承Django框架自带user模型类，自定义模型基类
    """用户模型类"""
    addr=models.CharField(max_length=200,null=True,blank=True,verbose_name='用户地址')
    phone=models.CharField(max_length=11,null=True,blank=True,verbose_name='用户电话')
    class Meta:  #元选项
        db_table='df_user'
        verbose_name='用户'    # 用于后台管理，别名
        verbose_name_plural=verbose_name   # 去除verbose_name后面自带的s

class AddressManage(models.Manager):
    """自定义收货地址模型管理器"""
    # 封装方法: 改变原有查询的结果集
    # 封装方法: 用于操作模型管理器对象所在模型类对应的数据表(增、删、改、查)
    def get_default_address(self,user):
        # 获取用户默认地址
        try:
            address=self.get(user=user,is_default=True)
        except self.model.DoesNotExist:
            address=None
        # 返回address
        return address

class Address(BaseModel):
    """收货地址模型类"""
    receiver=models.CharField(max_length=20,verbose_name='收件人')
    addr=models.CharField(max_length=200,verbose_name='收货地址')
    phone=models.CharField(max_length=11,verbose_name='联系电话')
    postcode=models.CharField(max_length=6,null=True,blank=True,verbose_name='邮编')
    user=models.ForeignKey('User',verbose_name='所属账户')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    objects=AddressManage()

    class Meta:
        db_table='df_address'
        verbose_name='收货地址'
        verbose_name_plural=verbose_name