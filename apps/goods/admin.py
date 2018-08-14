from django.contrib import admin
from django.core.cache import cache
from apps.goods.models import GoodsKind,IndexGoodsBanner,IndexPromotionBanner,GoodsSKU,GoodsSPU
# Register your models here.

#需要在后台数据的更新和增加时更新静态index页面
class BaseModelAdmin(admin.ModelAdmin):
    """父后台管理模型类"""
    def save_model(self, request, obj, form, change):
        #重写增方法
        super(admin.ModelAdmin,self).save_model(request, obj, form, change)
        #1.发起重新生成首页任务
        from celery_tasks.tasks import static_index
        static_index.delay()
        #2.删除首页缓存
        cache.delete('static_index_data')

    def delete_model(self, request, obj):
        #重写删方法
        super(BaseModelAdmin, self).delete_model(request, obj)
        from celery_tasks.tasks import static_index
        static_index.delay()
        cache.delete('static_index_data')

class GoodKindAdmin(BaseModelAdmin):
    """商品种类后台管理模型类"""
    pass

class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass

class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass

class GoodsSKUAdmin(BaseModelAdmin):
    pass

class GoodsSPUAdmin(BaseModelAdmin):
    pass

admin.site.register(GoodsKind,GoodKindAdmin) #商品种类
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin) # 首页促销活动
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin) #首页轮播
admin.site.register(GoodsSKU,GoodsSKUAdmin)  #商品详细
admin.site.register(GoodsSPU,GoodsSPUAdmin)  #商品小种类