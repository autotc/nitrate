# Generated by Django 3.2.16 on 2023-02-16 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tcms.core.models.base


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmt', '0002_auto_20230216_0237'),
    ]

    operations = [
        migrations.CreateModel(
            name='CmtPublicApi',
            fields=[
                ('api_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=32, verbose_name='公共api描述')),
                ('active_flag', models.BooleanField(default=True)),
                ('input', models.TextField(blank=True, null=True, verbose_name='请求信息')),
                ('output', models.TextField(blank=True, null=True, verbose_name='返回信息')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mypublicapis', to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publicapis', to='cmt.cmtservice')),
            ],
            options={
                'db_table': 'cmt_public_api',
            },
            bases=(models.Model, tcms.core.models.base.UrlMixin),
        ),
    ]