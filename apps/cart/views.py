from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from django.http.response import JsonResponse
from utils.mixin import LoginRequiredMixin
from apps.goods.models import GoodsSKU
# Create your views here.

# /cart/show   显示购物车页面
class CartShowView(LoginRequiredMixin,View):
    """显示购物车页面"""
    def get(self,request):
        # 获取购物车redis信息 cart_1: {'1':'2','3':'5'}
        user_id=request.user.id
        conn=get_redis_connection('default')
        cart_key='cart_%s'%user_id
        # 从redis中获取用户购物车商品的记录
        # cart_用户id : {'商品id': '商品数量'}
        # hgetall(key): 返回一个字典: {'商品id': '商品数量'}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        total_count = 0
        total_amount = 0
        # 获取对应商品的信息
        for sku_id, count in cart_dict.items():
            # 根据sku_id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)

            # 计算商品的小计
            amount = sku.price * int(count)

            # 给sku对象增加属性amount和count
            # 分别保存用户购物车中添加商品的小计和商品的数目
            sku.amount = amount
            sku.count = int(count)

            # 追加商品
            skus.append(sku)

            # 累加计算用户购物车中商品的总件数和总价格
            total_count += int(count)
            total_amount += amount
        content={
            'skus':skus,
            'total_count':total_count,
            'total_amount':total_amount
        }
        return render(request,'cart.html',content)

# 前端传递的参数: 商品id(sku_id) 商品数目(count）。
# url地址: '/cart/add'。
# 请求方式: 采用ajax post请求。
class CartAddView(View):
  """购物车记录添加"""
  def post(self, request):
      #判断用户是否登陆
    user=request.user
    if not user.is_authenticated():
        return JsonResponse({'res':0,'msg':'请先登陆'})
    # 获取前端数据
    sku_id=request.POST.get('sku_id')
    num=request.POST.get('num')
    #判断数据完整性
    if not all([sku_id,num]):
        return JsonResponse({'res':1,'msg':'数据不完整'})
    #判断商品id是否存在
    try:
        sku=GoodsSKU.objects.get(id=sku_id)
    except GoodsSKU.DoesNotExist as e:
        return JsonResponse({'res':2,'msg':'商品不存在'})
    #判断商品数量是否为数字
    try:
        count=int(num)
    except Exception as e:
        return JsonResponse({'res':3,'msg':'商品数量必须为有效数字'})
    # 业务处理：添加购物车记录
    # cart_2 : {'1':5, '3':2, '4':3}
    # 如果用户的购物车中已经添加过该商品，数目需要累加
    conn = get_redis_connection('default')

    # 拼接key
    cart_key = 'cart_%d'%user.id

    # hget(key, field): 如果field存在，返回field的值，否则返回None
    cart_count = conn.hget(cart_key, sku_id)

    if cart_count:
        # 数目累加
        count += int(cart_count)

    # 判断商品的库存
    if count > sku.stock:
        return JsonResponse({'res': 4, 'msg': '商品库存不足'})

    # 设置购物车中商品的数目
    # hset(key, field, value): 如果field存在则更新值，如果不存在则添加新属性
    conn.hset(cart_key, sku_id, count)

    # 获取用户购物车中商品的条目数
    cart_count = conn.hlen(cart_key)
    return JsonResponse({'res':5,'msg':'添加成功','cart_count':cart_count})

# 前端傳遞的參數：商品id（sku_id）
# url地址：‘/cart/delete’
# 請求方式：採用ajax post請求
class CartDeleteView(View):
    """購物車記錄刪除"""
    def post(self,request):
        # 判斷用戶是否已登陸
        user=request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0,'msg':'請先登陸'})
        # 獲取前端數據
        sku_id=request.POST.get('sku_id')
        # 校驗數據完整
        if not sku_id:
            return JsonResponse({'res': 1, 'msg': '數據不完整'})
        # 操作redis刪除數據，返回商品數量
        try:
            #不爲數字
            sku_id=int(sku_id)
            # 小於等於0
            if int(sku_id)<=0:
                return JsonResponse({'res': 2, 'msg': '數據錯誤'})
        except Exception as e:
            return JsonResponse({'res': 3, 'msg': '數據錯誤'})

        try:
            sku=GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 4, 'msg': '商品信息錯誤'})

        #拼接cart_key
        cart_key='cart_%d' % user.id
        conn=get_redis_connection('default')
        conn.hdel(cart_key,sku_id)
        cart_vals=conn.hvals(cart_key)
        total_count=0
        for val in cart_vals:
            total_count+=int(val)
        #返回應答
        return JsonResponse({'res': 5, 'msg': '刪除成功','total_count':total_count})

#前端傳遞的參數：商品id（sku_id）,商品數量count
#ajax post請求
# url地址：‘cart/update’
class CartUpdateView(View):
    """購物車數據修改視圖"""
    def post(self,request):
        #判斷用戶是否登陸
        user=request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0,'msg':'用戶未登錄'})
        #接收參數
        sku_id=request.POST.get('sku_id')
        count=request.POST.get('count')
        #校驗數據
        if not all([sku_id,count]):
            return JsonResponse({'res': 1, 'msg': '數據不完整'})
        #判斷該商品是否存在
        try:
            sku=GoodsSKU.objects.get(id=sku_id)

        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res': 2, 'msg': '商品信息錯誤'})
        #判斷是否是有效數字
        try:
            count=int(count)
        except Exception as e:
            return JsonResponse({'res': 3, 'msg': '商品數量必須是有效數字'})
        #判斷庫存是否足夠
        if count>sku.stock:
            return JsonResponse({'res': 4, 'msg': '庫存不足'})
        #修改redis數據庫
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        #更新數據
        conn.hset(cart_key,sku_id,count)
        cart_vals=conn.hvals(cart_key)
        total_count=0
        for val in cart_vals:
            total_count+=int(val)
        #返回應答
        return JsonResponse({'res': 5, 'msg': '更新數據庫成功','total_count':total_count})

