from django.db import models

class BaseModel(models.Model):
    """自定义models的基类"""
    creat_date=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updata_date=models.DateTimeField(auto_now=True,blank=True,null=True,verbose_name='修改时间')
    is_delete=models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        """自定义元选项"""
        abstract=True

