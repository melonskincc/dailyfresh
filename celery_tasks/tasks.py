# 导入celery类
from celery import Celery
from dailyfresh import settings
from django.core.mail import send_mail
from apps.goods.models import GoodsKind,IndexGoodsBanner,IndexPromotionBanner,IndexKindGoodsShow
from django.template import loader
import os
#创建celery对象
app=Celery('celery_tasks.tasks',broker='redis://192.168.72.54:6379/4')

#封装任务函数
@app.task
def send_register_active_email(to_email,username,token):
    """发送激活邮件"""
    # 组织邮件信息
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = """
            <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
            请点击一下链接激活您的账号(1小时之内有效)<br/>
            <a href="http://192.168.253.128:8000/user/active/%s">点击链接激活账户</a>
        """ % (username, token)

    # 发送激活邮件
    # send_mail(subject='邮件标题',
    #           message='邮件正文',
    #           from_email='发件人',
    #           recipient_list='收件人列表')
    # 模拟send_mail发送邮件时间
    # import time
    # time.sleep(5)
    send_mail(subject, message, sender, receiver, html_message=html_message)

@app.task
def static_index():
    """生产静态页面"""
    goods_kind = GoodsKind.objects.all()
    # 2.获取轮播图
    goods_banner = IndexGoodsBanner.objects.all()
    # 3.获取促销活动
    goods_promotion = IndexPromotionBanner.objects.all()
    # 3.获取商品分类,列表
    for kind in goods_kind:
        # 获取属于该种类的所有展示商品
        title_banner = IndexKindGoodsShow.objects.filter(goods_kind=kind, display_type=0)
        image_banner = IndexKindGoodsShow.objects.filter(goods_kind=kind, display_type=1)
        # 给该种类增加属性保存要显示的商品
        kind.title_banner = title_banner
        kind.image_banner = image_banner

    cart_count = 0
    # 组织上下文返回
    content = {
        'goods_kind': goods_kind,
        'goods_banner': goods_banner,
        'goods_promotion': goods_promotion,
        'cart_count': cart_count
    }
    # 加载模板
    temp=loader.get_template('static_index.html')
    #替换模板变量
    static_html=temp.render(content)
    #生成静态首页文件
    save_path=os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(static_html)