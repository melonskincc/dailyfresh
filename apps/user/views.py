from django.shortcuts import render,redirect
from apps.user.models import User,Address
from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo,OrderGoods
#导入视图类包
from django.views.generic import View
# 导入自定义登陆验证工具
from utils.mixin import LoginRequiredMixin
# 导入url反向解析的包
from django.core.urlresolvers import reverse
#导入用户认证，登陆，登出包
from django.contrib.auth import login,logout,authenticate
# 信息加密包
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
from dailyfresh import settings
#分页包
from django.core.paginator import Paginator
# 导入django_redis包
from django_redis import get_redis_connection
import re
# Create your views here.

# /user/register
class RegisterView(View):
    """注册页面类视图"""
    def get(self,request):
        #get 请求/显示页面
        return render(request,'register.html')

    def post(self,request):
        # 注册提交,后端校验
        # 获取注册信息
        username=request.POST.get('user_name')
        pwd=request.POST.get('pwd')
        email=request.POST.get('email')
        # 1.判断传来的数据是否为空
        if not all([username,pwd,email]):
            return render(request,'register.html',{'errmesg':'数据不能为空！'})

        # 2.判断用户是否已注册
        try:
            User.objects.get(username=username)
            # 已注册
            return render(request, 'register.html', {'errmesg': '用户已注册！'})
        except User.DoesNotExist as e :
            pass

        # 3.判断邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request, 'register.html', {'errmesg': '邮箱格式错误！'})
        # 4.判断邮箱是否已使用 TODO,项目测试阶段不用实现
        # 5.创建用户，改为未激活
        user=User.objects.create_user(username=username,password=pwd,email=email)
        user.is_active=0
        user.save()
        # 6.发邮件激活，可以用celery异步创建执行任务，解决用户因网络耗时操作的等待时间
        # 注册之后，需要给用户的注册邮箱发送激活邮件，在激活邮件中需要包含激活链接
        # 激活链接: /user/active/用户id
        # 存在问题: 其他用户恶意请求网站进行用户激活操作
        # 解决问题: 对用户的信息进行加密，把加密后的信息放在激活链接中，激活的时候在进行解密
        # /user/active/加密后token信息

        # 对用户的身份信息进行加密，生成激活token信息  过期时间1个小时
        serializer=Serializer(settings.SECRET_KEY,3600)
        info={"id":user.id}
        #返回bytes类型
        token=serializer.dumps(info)
        #str类型
        token=token.decode()
        # 使用celery发出发送邮件任务
        send_register_active_email.delay(email,username,token)
        # 7.跳转到首页
        return redirect(reverse("goods:index"))

# /user/active/加密token
class ActiveView(View):
    def get(self,request,token):
        # 激活,加载秘钥和过期时间
        serializer=Serializer(settings.SECRET_KEY,3600)
        try:
            #解密
            info=serializer.loads(token)
            #获取用户id
            user_id=info['id']
            #激活用户
            user=User.objects.get(id=user_id)
            user.is_active=1
            user.save()
            #跳转登陆页面
            return redirect(reverse("user:login"))
        except SignatureExpired as e:
            # 激活链接已失效
            # 实际开发：返回页面让你点击链接再发激活邮件
            return redirect(reverse("user:send_agin"))

# /user/login
class LoginView(View):
    """登陆页面视图类"""
    def get(self,request):
        # 请求登陆页面
        username=request.COOKIES.get('username')
        #判断用户是否记住用户名
        if username is None:
            checked=''
            username=''
        else:
            checked='checked'
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        # 登录校验
        username=request.POST.get('username')
        pwd=request.POST.get('pwd')
        remeber=request.POST.get('remember')
        url=request.GET.get('next')
        # 后端校验
        if not all([username,pwd]):
            return render(request,'login.html',{'errmesg':'用户名或密码不能为空！'})
        # 登陆校验
        user = authenticate(username=username, password=pwd) #返回值有俩，匹配成功返回User对象，否则返回None
        if user is not None:
            # 认证成功
            if user.is_active:
                # 用户激活
                #记住用户状态
                login(request,user)
                # 判断用户登陆之前是否输入过需要跳转的页面，如果是则跳转到用户需要页面，
                if url is None:
                    # 否则跳转首页
                    response=redirect(reverse("goods:index"))
                else:
                    response=redirect(url)
                # 设置session生命周期，默认两周，value=0表示关闭浏览器就清除。
                request.session.set_expiry(0)
                # 用户需要记住用户名
                if remeber=='on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    # 否则删除记录
                    response.delete_cookie('username')
                return response
            else:
                # 未激活
                return render(request, 'send_agin.html', {'errmesg': '账户未激活！','username':username})
        else:
            # 认证失败，返回错误消息
            return render(request,'login.html',{'errmesg':'用户名或密码错误！'})

#/user/send_agin
class SendAginView(View):
    """再次激活类视图"""
    def get(self,request):
        return render(request,'send_agin.html')

    def post(self,request):
        #获取用户名
        username=request.POST.get('username')
        # 获取到用户对象
        user=User.objects.get(username=username)
        # 判断用户是否已经激活
        if user.is_active==0:
            # 加密
            serializer=Serializer(settings.SECRET_KEY,3600)
            info={'id':user.id}
            token=serializer.dumps(info)
            token=token.decode()
            send_register_active_email.delay(user.email,user.username,token)
        return redirect('user:login')

#/user/logout 登出
class LogoutView(View):
    """登出业务逻辑类视图"""
    def get(self,request):
        # 清除登陆信息
        logout(request)
        #跳转到登陆
        return redirect(reverse("user:login"))

# /user       校验是否登陆，如果没登陆则没有权限访问该页面，跳转到校验默认页面
class UserInfoView(LoginRequiredMixin,View):
    """用户中心-信息页面"""
    def get(self,request):
        # 显示
        # 显示用户最近浏览信息  #TODO
        user=request.user   # 获取用户
        key='history_%s'%user.id
        conn=get_redis_connection('default')  # 获取redis链接
        view_list=conn.lrange(key,0,4)    # 获最新的5个浏览记录
        goods_list=[]
        for id in view_list:
            # 获取最近浏览商品对象
            goods_list.append(GoodsSKU.objects.get(id=id))
        address=Address.objects.get_default_address(user=request.user)
        return render(request, 'user_center_info.html', {'page': 'user','address':address,'goods_list':goods_list})

# /user/order/page
class UserOrderView(LoginRequiredMixin,View):
    """用户中心-订单视图类"""
    def get(self,request,page):
        #显示
        """
        前端需要的数据
        :param request: 订单信息表，订单商品信息表
        :return: render(request,'user_center_order.html',params)
        """
        user=request.user
        #1.获取订单信息
        orders=OrderInfo.objects.filter(user=user)
        #遍历订单获取订单商品信息
        for order in orders:
            sku_orders=OrderGoods.objects.filter(order=order)
            for sku_order in sku_orders:
                #每种商品小计
                sku_order.total_price=sku_order.count*sku_order.price

            #获取订单状态
            order.status_title=OrderInfo.ORDER_STATUS[order.status]
            #实付款
            order.total_pay=order.total_price+order.transit_price
            #给每个订单增加商品属性
            order.skus=sku_orders
        #分页处理
        paginator=Paginator(orders,1)
        page=int(page)
        #当前页大于总页数
        if page>paginator.num_pages:
            page=1
        #获取当前页所有对象
        order_page=paginator.page(page)
        #获取页码列表
        pages=paginator.page_range

        #组织上下文
        context={
            'page':'order',
            'order_page':order_page,
            'pages':pages
        }
        return render(request,'user_center_order.html',context)

# /user/address
class UserAddressView(LoginRequiredMixin,View):
    """用户中心-收货地址类视图"""
    def get(self,request):
        # 显示
        # 获取登录用户user
        user = request.user
        address = Address.objects.get_default_address(user)  #TODO ,Address模型类中自定义管理器。
        # 组织模板上下文
        context = {
            'address': address,
            'page': 'address'
        }

        # 使用模板
        return render(request, 'user_center_site.html', context)

    def post(self,request):
        # 获取数据
        receiver=request.POST.get('receiver')
        addr=request.POST.get('addr')
        post_code=request.POST.get('post_code')
        phone=request.POST.get('phone')
        user=request.user
        address=Address.objects.get_default_address(user=user)
        is_default=True
        if address is not None:
            is_default=False
        # 参数校验
        if not all([receiver,addr,phone]):

            return render(request,'user_center_site.html',{"errmesg":"数据不完整！","address":address})
        if not re.match(r'^[1][3,4,5,7,8][0-9]{9}$',phone):
            return render(request, 'user_center_site.html', {"errmesg": "手机号错误！","address":address})
        Address.objects.create(receiver=receiver,
                               addr=addr,
                               postcode=post_code,
                               user=user,
                               is_default=is_default,
                               phone=phone)
        # 返回应答刷新页面
        return redirect(reverse("user:address"))