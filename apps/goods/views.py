from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
#分页处理包
from django.core.paginator import Paginator
from apps.goods.models import GoodsSKU,GoodsKind,IndexGoodsBanner,IndexPromotionBanner,IndexKindGoodsShow
from apps.order.models import OrderGoods
from django_redis import get_redis_connection
from haystack.urls import SearchView
# Create your views here.

# /index
class IndexView(View):
    """首页类视图"""
    def get(self,request):
        # 1.获取全部商品分类
        goods_kind=GoodsKind.objects.all()
        # 2.获取轮播图
        goods_banner=IndexGoodsBanner.objects.all()
        # 3.获取促销活动
        goods_promotion=IndexPromotionBanner.objects.all()
        # 3.获取商品分类,列表
        for kind in goods_kind:
            # 获取属于该种类的所有展示商品
            title_banner=IndexKindGoodsShow.objects.filter(goods_kind=kind,display_type=0)
            image_banner=IndexKindGoodsShow.objects.filter(goods_kind=kind,display_type=1)
            # 给该种类增加属性保存要显示的商品
            kind.title_banner=title_banner
            kind.image_banner=image_banner
        # 4.如果用户登陆了，获取购物车信息redis，没登陆设为0
        cart_count=0
        if request.user.is_authenticated():
            # 获取redis链接
            conn=get_redis_connection('default')
            # 获取所有购物车信息 key:cart_id ----value:hash{商品id,数量}，hlen(key)获取长度
            cart_key='cart_%s'%request.user.id
            cart_count=conn.hlen(cart_key)

        # 组织上下文返回
        content={
            'goods_kind':goods_kind,
            'goods_banner':goods_banner,
            'goods_promotion':goods_promotion,
            'cart_count':cart_count
        }
        return render(request,'index.html',content)

# /goods/detail/goods_id
class GoodsDetailView(View):
    """商品详情视图"""
    def get(self,request,id):
        # 用户不为空,
        user=request.user
        try:
            # 获取商品对象
            sku = GoodsSKU.objects.get(id=id)
            # 获取商品分类的信息
            types = GoodsKind.objects.all()
            # 获取商品的评论信息
            order_skus = OrderGoods.objects.filter(goods_sku=sku).exclude(comment='').order_by('-updata_date')

            # 获取和商品同一个SPU的其他规格的商品
            same_spu_skus = GoodsSKU.objects.filter(goods_spu=sku.goods_spu).exclude(id=id)

            # 获取和商品同一种类的两个新品信息
            new_skus = GoodsSKU.objects.filter(goods_kind=sku.goods_kind).order_by('-creat_date')[:2]
            cart_count=0
            if user:
                # 则在其的redis中添加一个新的浏览记录。redis中key=history_id,值=[商品id1,商品id2]
                conn=get_redis_connection('default')
                key='history_%s'%user.id
                # 先尝试从redis对应列表中移除sku_id
                # lrem(key, count, value) 如果存在就移除，如果不存在什么都不做
                conn.lrem(key, 0, id)

                # 只保存用户最新浏览的5个商品的id
                # ltrim(key, start, stop)
                conn.ltrim(key, 0, 4)

                # 加入新的浏览记录
                conn.lpush(key,sku.id)
                #获取redis中购物车商品数量
                cart_key='cart_%s'%user.id
                cart_count = conn.hlen(cart_key)

            #组织上下文
            content={
                'sku':sku,
                'types':types,
                'order_skus': order_skus,
                'same_spu_skus': same_spu_skus,
                'new_skus': new_skus,
                'cart_count': cart_count
            }
            return render(request,'detail.html',content)
            # 直接返回图片详情页

        except GoodsSKU.DoesNotExist as e:
            #商品不存在,返回首页
            return redirect(reverse("goods:index"))


# /goods/list/kind_id/page?sort=排序方式
class GoodsListView(View):
    """显示所有同种类商品类视图"""
    def get(self,request,id,page):
        try:
            kind=GoodsKind.objects.get(id=id)
        except GoodsKind.DoesNotExist as e:
            return redirect(reverse("goods:index"))
        #获取所有种类数据
        types=GoodsKind.objects.all()
        #获取新品
        new_list=GoodsSKU.objects.filter(goods_kind=id).order_by('-creat_date')[:2]
        #获取用户
        user=request.user
        #获取排序方式
        sort=request.GET.get('sort')
        # 获取id种类的商品信息
        if sort == 'price':
            skus = GoodsSKU.objects.filter(goods_kind=id).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(goods_kind=id).order_by('-sales')
        else:
            # 按照默认顺序来排序
            sort = 'default'
            skus = GoodsSKU.objects.filter(goods_kind=id).order_by('-id')

        #分页操作
        paginator=Paginator(skus,1)
        page=int(page)
        if page > paginator.num_pages:
            # 默认获取第1页的内容
            page = 1
         # 获取第page页内容, 返回Page类的实例对象
        goods_page = paginator.page(page)
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 1-num_pages
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            # num_pages-4, num_pages
            pages = range(num_pages - 4, num_pages + 1)
        else:
            # page-2, page+2
            pages = range(page - 2, page + 3)
        #获取购物车商品数量
        cart_count=0
        if user.is_authenticated():
            conn=get_redis_connection('default')
            cart_key='cart_%d'%user.id
            cart_count=conn.hlen(cart_key)

        content={
            'cart_count':cart_count,
            'new_list':new_list,
            'types':types,
            'goods_page':goods_page,
            'sort':sort,
            'pages':pages,
            'kind':kind
        }
        return render(request,'list.html',content)
