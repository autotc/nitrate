# Generated by Django 3.2.16 on 2023-02-17 06:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmt', '0006_cmtapi_api_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmtapidata',
            name='api',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apiData', to='cmt.cmtapi'),
        ),
        migrations.DeleteModel(
            name='CmtPublicApi',
        ),
    ]