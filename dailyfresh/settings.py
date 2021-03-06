"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's8hc*rp741*-lb5-%xnhoe*f**a5f4bney(phs_m1a9n1stg0j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUT=False
ALLOWED_HOSTS = []
# ALLOWED_HOSTS=['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.user', # 注册用户应用
    'apps.order', # 注册订单应用
    'apps.goods', # 注册商品应用
    'apps.cart', # 注册购物车应用
    'haystack', #注册全文检索框架
    'debug_toolbar',#注册调试助手
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # debug助手
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'

#DEBUG 工具框
INTERNAL_IPS = ("127.0.0.1",)
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'HOST':'192.168.72.54',
        'USER':'cgh',
        'PASSWORD':'123456',
        'PORT':3306
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# 配置静态文件存放路径
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]

#使用邮箱发邮件设置
EMAIL_USE_SSL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
#发送邮件的邮箱
EMAIL_HOST_USER = '954182252@qq.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'pjiolbgmndilbefe'
#收件人看到的发件人
EMAIL_FROM = 'ChenGuangHai<954182252@qq.com>'

# 指定django认证系统使用的用户模型类
AUTH_USER_MODEL='user.User'

# # session存到redis配置
# SESSION_ENGINE = 'redis_sessions.session'
# SESSION_REDIS_HOST = 'localhost'
# SESSION_REDIS_PORT = 6379
# SESSION_REDIS_DB = 2
# SESSION_REDIS_PASSWORD = ''
# SESSION_REDIS_PREFIX = 'session'

#配置富文本编辑器
TINYMCE_DEFAULT_CONFIG={
    'theme':'advanced',
    'width':600,
    'height':400,
}

# 配置login_required装饰器登陆校验不成功，表示没登陆跳转到登陆页面
LOGIN_URL='/user/login'

# 设置Django框架的缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 设置django缓存的数据保存在redis数据库中
        "LOCATION": "redis://127.0.0.1:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Django的session存储设置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 设置session信息存储在CACHES配置项default对应的redis中
SESSION_CACHE_ALIAS = "default"

# 指定Django保存文件使用的文件存储类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDfsStorage'

# 指定FDFS客户端配置文件的路径
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fdfs/client.conf')

# 指定FDFS系统中Nginx的ip和port
FDFS_NGINX_URL = 'http://192.168.253.128:8888/'

#配置全文检索
HAYSTACK_CONNECTIONS = {
    'default': {
        #使用whoosh引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        #索引文件路径
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}
#当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

#配置alipay网站支付初始化数据
#应用id
ALIPAY_APP_ID=2016091200491846
#默认回调url，默认None,项目上线到公网的时候才用
ALIPAY_NOTIFY_URL=None
#alipay公钥
ALIPAY_PUBLICK_KEY_PATH=os.path.join(BASE_DIR,'apps/order/ailpay_public_key.pem')
#应用私钥
APP_PRIVATE_KEY_PATH=os.path.join(BASE_DIR,'apps/order/app_private_key.pem')
#数据加密算法
SIGN_TYPE="RSA2"
#Flase代表线上环境.True代表沙箱环境
ALIPAY_DEBUG=True