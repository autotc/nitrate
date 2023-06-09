# Generated by Django 3.2.16 on 2023-02-09 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tcms.core.models.base


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CmtService',
            fields=[
                ('service_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, verbose_name='服务器名称')),
                ('env_type', models.CharField(max_length=8, verbose_name='环境')),
                ('address', models.TextField(db_column='address', verbose_name='ip:port')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_column='create_date', verbose_name='创建时间')),
            ],
            options={
                'db_table': 'cmt_service',
            },
            bases=(models.Model, tcms.core.models.base.UrlMixin),
        ),
        migrations.CreateModel(
            name='CmtApi',
            fields=[
                ('api_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=32, verbose_name='api描述')),
                ('endpoint', models.CharField(max_length=64, null=True, verbose_name='url')),
                ('common_flag', models.BooleanField(db_index=True, default=False)),
                ('run_way', models.TextField(null=True, verbose_name='运行方式')),
                ('input', models.TextField(blank=True, null=True, verbose_name='请求信息')),
                ('output', models.TextField(blank=True, null=True, verbose_name='返回信息')),
                ('tag', models.CharField(max_length=32, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='myapis', to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apis', to='cmt.cmtservice')),
            ],
            options={
                'db_table': 'cmt_api',
            },
            bases=(models.Model, tcms.core.models.base.UrlMixin),
        ),
    ]
