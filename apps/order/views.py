from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse,HttpResponse
from utils.mixin import LoginRequiredMixin
from django.views.generic import View
from apps.goods.models import GoodsSKU
from apps.user.models import Address
from apps.order.models import OrderGoods,OrderInfo
from django_redis import get_redis_connection
from django.db import transaction
from datetime import datetime
#导入支付包sdk包
from alipay import AliPay
from django.conf import settings
# Create your views here.

# /cart/palce
class PlaceOrderView(LoginRequiredMixin,View):
    """提交订单页面"""
    def get(self,request):
        #判断用户登陆跳转到购物车
        user=request.user
        if user.is_authenticated():
            return redirect(reverse("cart:show"))
        #未登录跳转到登陆页面
        return redirect(reverse("user:login"))

    def post(self,request):
        #判断是哪里提交过来的数据1.cart表示购物车，detail表示详情页
        user=request.user
        # 1.所有收货地址
        try:
            address = Address.objects.filter(user=user)
        except Address.DoesNotExist as e:
            return redirect(reverse("user:address"))
        #所有购买商品对象
        skus=[]
        #总价格
        total_price=0
        # 商品总数
        total_count=0
        comit_addr=request.POST.get('comit_addr')
        #从购物车跳过来的数据
        if comit_addr=='cart':
            # 接收参数，商品id
            ids = request.POST.getlist('sku_ids')
            #获取redis中该id商品的购买数量
            conn=get_redis_connection('default')
            cart_key='cart_%d'%user.id
            #获取购物车所有商品id
            for id in conn.hkeys(cart_key):
                id=id.decode()
                #购买的商品
                if id in ids:
                    #获取购买数量
                    count=conn.hget(cart_key,id)
                    sku=GoodsSKU.objects.get(id=id)
                    #小计
                    sku.total_price=int(count)*sku.price
                    sku.total_count=count
                    total_price+=sku.total_price
                    total_count+=int(count)
                    skus.append(sku)
        else:
            #detail提交过来的数据
            count=request.POST.get('count')
            ids=request.POST.get('sku_id')
            sku=GoodsSKU.objects.get(id=ids)
            sku.total_count=count
            sku.total_price=int(count)*sku.price
            total_price=sku.total_price
            total_count=count
            skus.append(sku)
        #发给前端的数据
        #3.运费，总金额，实付款
        transit_price=10
        #实付款
        total_pay=transit_price+total_price
        #5.组织上下文
        context={
            'address':address,
            'skus':skus,
            'total_count':total_count,
            'total_price':total_price,
            'total_pay':total_pay,
            'transit_price':transit_price,
            'sku_ids':','.join(ids),
            'comit_addr':comit_addr
        }
        return render(request,'place_order.html',context)


#/order/create  前端ajax提交请求 创建订单
class CreateOrderView(LoginRequiredMixin,View):
    """创建订单视图类（防止高并发，使用悲观锁---冲突多时使用）
        使用事物，成功提交，不成功，回滚数据
    """
    @transaction.atomic      #开始事物
    def post(self,request):
        #校验数据
        user=request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0,'msg':'用户未登录'})

        #2.获取地址
        addr_id=request.POST.get('addr_id')
        #5.支付方式
        pay_method=request.POST.get('pay_method')
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 1, 'msg': '支付方式错误'})
        #获取商品id
        sku_ids=request.POST.get('sku_ids').split(',')
        if not all([addr_id,pay_method,sku_ids]):
            return JsonResponse({'res': 2, 'msg': '数据不完整'})

        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist as e:
            return JsonResponse({'res': 3, 'msg': '地址信息错误'})

        #1.订单编号：20180316145420日期秒+用户id
        order_id=datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)
        #3.获取邮费
        transit_price=10
        #4.总价，总数量
        total_count=0
        total_price=0
        #设置事务保存点
        s1=transaction.savepoint()
        #创建订单表
        try:
            order=OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=addr,
                transit_price=transit_price,
                total_count=total_count,
                total_price=total_price,
                pay_method=pay_method
            )
            #6.1获取商品
            #6.2获取小计数量
            #6.3获取价格
            #6.创建订单商品表
            comit_addr=request.POST.get('comit_addr')
            conn=get_redis_connection('default')
            cart_key='cart_%d'%user.id
            for sku_id in sku_ids:
                try:
                    print('用户: %s 尝试获取锁' % user.username)
                    #加锁
                    sku=GoodsSKU.objects.select_for_update().get(id=sku_id)
                    print('用户: %s 成功获取锁' % user.username)
                except GoodsSKU.DoesNotExist as e:
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'res': 4, 'msg': '商品信息错误'})
                if comit_addr=='cart':
                    count=conn.hget(cart_key,sku_id)
                else:
                    count=request.POST.get('count')
                count=int(count)
                #判断库存是否足够
                if count>sku.stock:
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'res': 5, 'msg': '商品库存不足'})

                #模拟高并发
                # import time
                # time.sleep(10)

                #总价，总数量
                total_count+=count
                total_price+=count*sku.price
                order_sku=OrderGoods.objects.create(
                    order=order,
                    goods_sku=sku,
                    count=count,
                    price=sku.price
                )
                #7.提交成功该商品销量增加，库存减少
                sku.stock-=count
                sku.sales+=count
                sku.save()
            #更新订单中的总价和总数量
            order.total_count=total_count
            order.total_price=total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(s1)
            return JsonResponse({'res':6,'msg':'创建订单失败'})
        # 8.删除redis购物车该商品的缓存
        if comit_addr=='cart':
            conn.hdel(cart_key,*sku_ids)
        #返回应答
        return JsonResponse({'res': 7, 'msg': '订单创建成功'})

#/order/pay   用户付款
class PayOrderView(LoginRequiredMixin,View):
    """订单支付视图类"""
    def post(self,request):
        """
        :param request: 1.order_id用户订单编号
        :return: 支付宝付款页面:https://openapi.alipay.com/gateway.do? + order_string
        order_string:支付宝接口需要的参数
        """
        user=request.user
        #1.获取需要付款的订单号
        order_id=request.POST.get('order_id')
        #校验数据
        if not all([order_id]):
            return JsonResponse({'res':0,'msg':'数据不完整'})
        #校验订单是否存在,并且状态是未支付
        try:
            order=OrderInfo.objects.get(order_id=order_id,status=1,user=user)
        except OrderInfo.DoesNotExist as e:
            return JsonResponse({'res':1,'msg':'订单信息错误'})
        if order.pay_method==1:
            print('货到付款')
        elif order.pay_method==2:
            print('微信支付')
        elif order.pay_method==3:
            #公共参数部分初始化
            alipay=AliPay(
                appid=settings.ALIPAY_APP_ID,
                app_notify_url=settings.ALIPAY_NOTIFY_URL,
                app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
                alipay_public_key_path=settings.ALIPAY_PUBLICK_KEY_PATH,
                sign_type=settings.SIGN_TYPE,
                debug=settings.ALIPAY_DEBUG
            )
            #组织支付宝接口参数
            total_amount=order.total_price+order.transit_price
            # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_id,  # 商户订单号
                total_amount=str(total_amount),  # 订单总金额
                subject="天天生鲜测试订单:%s"%order_id,  # 订单标题
                return_url="http://192.168.253.128:8000/order/check",
                #notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
            )
            re_url='https://openapi.alipaydev.com/gateway.do?'+order_string
            return JsonResponse({'res':2,'msg':re_url})
        else:
            print('银联支付')

#/order/check  返回支付宝交易号和交易数据
class OrderCheckView(LoginRequiredMixin,View):
    """校验支付结果视图类"""
    def get(self,request):
        """
        获取支付宝支付成功返回的参数
        :param request: trade_no支付宝流水号,out_trade_no订单号
        :return: pay_result.html,
        """
        user=request.user
        trade_no=request.GET.get('trade_no')
        order_id=request.GET.get('out_trade_no')
        #校验参数完整性
        if not all([trade_no,order_id]):
            return HttpResponse('参数不完整')

        #订单增加支付宝流水号，修改订单状态实际中待发货，现在为待评价
        try:
            order=OrderInfo.objects.get(
                user=user,
                order_id=order_id,
                status=1,
                pay_method=3,)
        except OrderInfo.DoesNotExist:
            return HttpResponse('订单信息错误')

        #初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL,
            app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLICK_KEY_PATH,
            sign_type=settings.SIGN_TYPE,
            debug=settings.ALIPAY_DEBUG
        )
        # 调用阿里账单查询接口
        response=alipay.api_alipay_trade_query(trade_no=trade_no)
        code=response.get('code') #阿里返回的网关码，10000表示成功
        status=response.get('trade_status') #订单的状态，TRADE_SUCCESS：表示交易成功
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        cart_count=conn.hlen(cart_key)   #TODO:获取购物车总数
        if code=="10000" and status=="TRADE_SUCCESS":
            order.trande_no=trade_no
            order.status=4
            order.save()
            return render(request, 'pay_result.html', {'pay_result': '支付成功','cart_count':cart_count})
        else:
            return render(request,'pay_result.html',{'pay_result':'支付失败','cart_count':cart_count})

#/order/comment/order_id 评论页面
class OrderCommentView(LoginRequiredMixin,View):
    """商品评价视图类"""
    def get(self,request,order_id):
        """
        :param request: order_id订单号
        :return: order_comment.html页面，request，order_skus订单商品
        """
        user=request.user
        #校验数据完整性
        if not all([order_id]):
            return redirect(reverse('user:order', kwargs={"page": 1}))
        try:
            order=OrderInfo.objects.get(user=user,order_id=order_id,status=4)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('user:order', kwargs={"page": 1}))

        order.status_name=order.ORDER_STATUS[order.status]
        #获取所有商品
        order_skus=OrderGoods.objects.filter(order=order)
        for sku in order_skus:
            #计算总价
            sku.amount=sku.count*sku.price
        order.order_skus=order_skus
        return render(request,'order_comment.html',{'order':order})

    def post(self,request,order_id):
        """
        :param request: 获取评论信息content，获取商品id：sku_1....
        :return: 返回订单页面
        """
        user=request.user
        if not order_id:
            return HttpResponse('数据不完整')
        #获取订单
        try:
            order=OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return HttpResponse('订单信息错误')
        #获取总数
        total_count=request.POST.get('total_count')
        for i in range(1,int(total_count)+1):
            #获取商品id
            id='sku_%d'%i
            sku_id=request.POST.get(id)
            #获取评论信息
            content='content_%d'%i
            comment=request.POST.get(content)
            #获取对应的订单商品表
            try:
                order_sku=OrderGoods.objects.get(order=order,goods_sku=sku_id)
            except OrderGoods.DoesNotExist:
                return HttpResponse('商品信息错误')
            #提交评论
            order_sku.comment=comment
            order_sku.save()
        #更改订单状态为已完成
        order.status=5
        order.save()
        #返回订单页面
        return redirect(reverse("user:order",args=[1,]))
