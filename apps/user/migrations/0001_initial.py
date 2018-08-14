# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', error_messages={'unique': 'A user with that username already exists.'}, max_length=30)),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('addr', models.CharField(max_length=200, blank=True, null=True, verbose_name='用户地址')),
                ('phone', models.CharField(max_length=11, blank=True, null=True, verbose_name='用户电话')),
                ('groups', models.ManyToManyField(related_name='user_set', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', blank=True, verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission', blank=True, verbose_name='user permissions')),
            ],
            options={
                'db_table': 'df_user',
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creat_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updata_date', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('receiver', models.CharField(max_length=20, verbose_name='收件人')),
                ('addr', models.CharField(max_length=200, verbose_name='收货地址')),
                ('phone', models.CharField(max_length=11, verbose_name='联系电话')),
                ('postcode', models.CharField(max_length=6, verbose_name='邮编')),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='所属账户')),
            ],
            options={
                'db_table': 'df_address',
                'verbose_name': '收货地址',
                'verbose_name_plural': '收货地址',
            },
        ),
    ]
